import logging
from statistics import median

from espn_api.football import League as EspnLeague
from espn_api.football import Team as EspnTeam
from espn_api.football.box_score import BoxScore as EspnBoxScore

from ..models import League, Team, Division, Matchup


class RefreshStandings:

    def __init__(self, league: League):
        self.logger = logging.getLogger(__name__)
        self.__league = league
        self.__espn_league = self.__build_espn_league(league)
        self.__league_id = league.espn_id

    def refresh(self):
        self.__update_league()
        self.__update_teams()
        self.__update_matchups()

    @staticmethod
    def __build_espn_league(league: League):
        return EspnLeague(league_id=league.espn_id,
                          year=league.league_year,
                          espn_s2=league.espn_s2,
                          swid=league.swid)

    def __update_league(self):
        self.__league.current_week = self.__espn_league.current_week
        self.__league.nfl_week = self.__espn_league.nfl_week
        self.__league.save()

    def __update_teams(self):
        espn_teams = self.__espn_league.teams
        self.logger.debug(f"Updating {len(espn_teams)} teams for league {self.__league_id}")
        for espn_team in espn_teams:
            self.__update_team(espn_team)

    def __update_team(self, espn_team: EspnTeam):
        try:
            team = self.__get_team(espn_team)
            self.logger.debug(f"Found team {team.name}")
        except Team.DoesNotExist:
            self.logger.info(f"Team {espn_team.team_id}:{espn_team.team_name} does not exist")
            team = self.__create_team(espn_team)

        team.name = espn_team.team_name
        team.wins = espn_team.wins
        team.losses = espn_team.losses
        team.points_for = espn_team.points_for
        team.save()

    def __get_team(self, espn_team: EspnTeam):
        return Team.objects.get(espn_id=espn_team.team_id,
                                division__league__espn_id=self.__league_id)

    def __create_team(self, espn_team: EspnTeam):
        self.logger.info(f"Creating team {espn_team.team_name} league {self.__league.espn_id}")
        d = self.__get_or_create_division(espn_team.division_id, espn_team.division_name)
        team = Team(
            division=d,
            espn_id=espn_team.team_id,
            name=espn_team.team_name
        )
        team.save()
        return team

    def __get_or_create_division(self, espn_division_id, espn_division_name):
        """Gets or Creates a division by espn_id and updates its name."""
        try:
            d = Division.objects.get(espn_id=espn_division_id,
                                     league__espn_id=self.__league.espn_id)
            if d.name != espn_division_name:
                d.name = espn_division_name
                d.save()
        except Division.DoesNotExist:
            self.logger.info(f"Division {espn_division_name} in "
                             f"league {self.__league.espn_id} doesn't exist")
            d = Division(
                espn_id=espn_division_id,
                name=espn_division_name,
                league=self.__league
            )
            d.save()

        return d

    def __max_completed_week(self):
        num_reg_season_weeks = self.__espn_league.settings.reg_season_count
        current_week = self.__espn_league.current_week
        if num_reg_season_weeks > current_week:
            return current_week
        else:
            return num_reg_season_weeks

    def __update_matchups(self):
        for cur_week in range(1, self.__max_completed_week()):
            self.logger.info(f'Updating matchups for league {self.__league_id} week {cur_week}')
            box_scores = self.__espn_league.box_scores(cur_week)
            for box_score in box_scores:
                self.__update_matchup(box_score, cur_week)

            self.__update_victory_points(cur_week)

    def __update_matchup(self, box_score: EspnBoxScore, week: int):
        try:
            m = Matchup.objects.get(week=week,
                                    home_team__espn_id=box_score.home_team.team_id,
                                    home_team__division__league__espn_id=self.__league_id,
                                    away_team__espn_id=box_score.away_team.team_id,
                                    away_team__division__league__espn_id=self.__league_id)
            if m.home_score != box_score.home_score or m.away_score != box_score.away_score:
                # only update the matchup if the scores changed
                self.logger.info(f'Updating matchup {m.id} week {week}:'
                                 f' {m.home_team.name} @ {m.away_team.name}')
                m.home_score = box_score.home_score
                m.away_score = box_score.away_score
                m.save()
        except Matchup.DoesNotExist:
            # Matchup does not exist, create it
            ht = self.__get_team(box_score.home_team)
            at = self.__get_team(box_score.away_team)
            m = Matchup(
                week=week,
                home_team=ht,
                away_team=at,
                home_score=box_score.home_score,
                away_score=box_score.away_score
            )
            m.save()

    def __update_victory_points(self, week: int):
        self.logger.info(f'Updating victory_points for league {self.__league_id} week {week}')
        matchups = Matchup.objects.filter(week=week,
                                          home_team__division__league__espn_id=self.__league_id)
        week_scores = matchups.values_list('home_score', flat=True)\
            .union(matchups.values_list('away_score', flat=True))
        median_score = median(week_scores)
        max_score = max(week_scores)

        for matchup in matchups:
            if matchup.home_score >= matchup.away_score:
                matchup.home_vp = self.win_vp(matchup.home_score, max_score)
                matchup.away_vp = self.loss_vp(matchup.away_score, median_score)
            else:
                matchup.home_vp = self.loss_vp(matchup.home_score, median_score)
                matchup.away_vp = self.win_vp(matchup.away_score, max_score)
            matchup.save()

    @staticmethod
    def win_vp(score, max_score):
        if score == max_score:
            return 3
        else:
            return 2

    @staticmethod
    def loss_vp(score, median_score):
        if score > median_score:
            return 1
        else:
            return 0
