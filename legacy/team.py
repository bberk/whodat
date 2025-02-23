import re

from espn_api.football import Team as EspnTeam


class Team:

    def __init__(self, espn_team: EspnTeam, league):
        self.__team = espn_team
        self.__league = league
        self.__team_id = espn_team.team_id
        self.__team_name = self.sanitize_team_name(espn_team.team_name)
        self.__wins = 0
        self.__losses = 0
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
        vp = 0
        if week_num != self.__league.get_cup_week():
            vp += 1
            self.__wins += 1

        if score == week_max:
            vp += 2
        elif score > week_median:
            vp += 1

        self.__victory_points[self.week_to_str(week_num)] = vp

    def add_loss(self, week_num, score):
        week_min = self.__league.get_week_min(week_num)
        week_median = self.__league.get_week_median(week_num)
        if week_num != self.__league.get_cup_week():
            self.__losses += 1

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
            'wins': self.__wins,
            'losses': self.__losses,
            'weekly_victory_points': self.__victory_points,
            'points for': self.__team.points_for
        }

    @staticmethod
    def sanitize_team_name(team_name: str):
        return re.compile(r"\s+").sub(" ", team_name).strip()
