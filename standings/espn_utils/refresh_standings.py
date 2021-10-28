import logging

from espn_api.football import League as EspnLeague
from espn_api.football import Team as EspnTeam

from ..models import League, Team, Division


class RefreshStandings:

    def __init__(self, league: League):
        self.logger = logging.getLogger(__name__)
        self.__league = league
        self.__espn_league = self.__build_espn_league(league)
        self.__league_id = league.espn_id

    def refresh(self):
        self.__update_league()
        self.__update_teams()

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
        self.logger.debug("Updating {} teams for league {}".format(len(espn_teams),
                                                                   self.__league_id))
        for espn_team in espn_teams:
            self.__update_team(espn_team)

    def __update_team(self, espn_team: EspnTeam):
        try:
            team = Team.objects.get(espn_id=espn_team.team_id,
                                    division__league__espn_id=self.__league_id)
            self.logger.debug("Found team {}".format(team.name))
        except Team.DoesNotExist:
            self.logger.info("Team {}:{} does not exist".format(espn_team.team_id,
                                                                espn_team.team_name))
            team = self.__create_team(espn_team)

        team.wins = espn_team.wins
        team.losses = espn_team.losses
        team.points_for = espn_team.points_for
        team.save()

    def __create_team(self, espn_team: EspnTeam):
        self.logger.info("Creating team {} league {}".format(espn_team.team_name,
                                                             self.__league.espn_id))
        d = self.__get_division(espn_team.division_id, espn_team.division_name)
        team = Team(
            division=d,
            espn_id=espn_team.team_id,
            name=espn_team.team_name
        )
        team.save()
        return team

    def __get_division(self, espn_division_id, espn_division_name):
        """Gets or Creates a division by espn_id and updates its name."""
        try:
            d = Division.objects.get(espn_id=espn_division_id,
                                     league__espn_id=self.__league.espn_id)
            if d.name != espn_division_name:
                d.name = espn_division_name
                d.save()
        except Division.DoesNotExist:
            self.logger.info("Division {} in league {} doesn't exist".format(espn_division_name,
                                                                             self.__league.espn_id))
            d = Division(
                espn_id=espn_division_id,
                name=espn_division_name,
                league=self.__league
            )
            d.save()

        return d
