from espn_api.football import Team as EspnTeam


class Team:

    def __init__(self, espn_team: EspnTeam, league):
        self.__team = espn_team
        self.__league = league
        self.__team_id = espn_team.team_id
        self.__team_name = espn_team.team_name
        self.__victory_points = {}  # dict of week_number -> victory_points

    def get_division_id(self):
        return self.__team.division_id

    def get_division_name(self):
        return self.__team.division_name

    def add_win(self, week_num, score):
        week_max = self.__league.get_week_max(week_num)
        if week_max == score:
            self.__victory_points[week_num] = 3
        else:
            self.__victory_points[week_num] = 2

    def add_loss(self, week_num, score):
        week_median = self.__league.get_week_median(week_num)
        if score > week_median:
            self.__victory_points[week_num] = 1
        else:
            self.__victory_points[week_num] = 0

    def to_pandas_row(self):
        return {
            'team_id': self.__team_id,
            'team': self.__team_name,
            'division_id': self.__team.division_id,
            'division_name': self.__team.division_name,
            'wins': self.__team.wins,
            'losses': self.__team.losses,
            'weekly_victory_points': self.__victory_points,
            'points for': self.__team.points_for
        }
