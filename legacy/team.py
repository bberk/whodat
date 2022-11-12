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

    @staticmethod
    def week_to_str(week_num):
        return '\033[95m' + str(week_num) + '\033[0m'

    def add_win(self, week_num, score):
        week_max = self.__league.get_week_max(week_num)
        week_median = self.__league.get_week_median(week_num)
        if score == week_max:
            self.__victory_points[self.week_to_str(week_num)] = 3
        elif score > week_median:
            self.__victory_points[self.week_to_str(week_num)] = 2
        else:
            self.__victory_points[self.week_to_str(week_num)] = 1

    def add_loss(self, week_num, score):
        week_min = self.__league.get_week_min(week_num)
        week_median = self.__league.get_week_median(week_num)
        if score > week_median:
            self.__victory_points[self.week_to_str(week_num)] = 1
        elif score == week_min:
            self.__victory_points[self.week_to_str(week_num)] = -1
        else:
            self.__victory_points[self.week_to_str(week_num)] = 0

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
