from statistics import median

import numpy as np
import pandas as pd
from espn_api.football import League as EspnLeague
from espn_api.football.box_score import BoxScore as EspnBoxScore
from espn_api.football.box_player import BoxPlayer

from team import Team


class League:

    def __init__(self, espn_league: EspnLeague, cup_week: int):
        self.__league = espn_league
        self.__cup_week = cup_week
        self.__divisions = {}  # dict of division_id -> division_name
        self.__all_teams = {}  # dict of team_id -> Team
        self.__median_scores = {}  # dict of week_num -> median_score
        self.__max_scores = {}  # dict of week_num -> max_score
        self.__min_scores = {}  # dict of week_num -> min_score
        self.__build_teams()
        self.__build_divisions()

    def get_cup_week(self):
        return self.__cup_week

    def __build_teams(self):
        for espnTeam in self.__league.teams:
            team = Team(espnTeam, self)
            self.__all_teams[espnTeam.team_id] = team

    def __build_divisions(self):
        for team in self.__all_teams.values():
            self.__divisions[team.get_division_id()] = team.get_division_name()

    def get_week_max(self, week_num):
        return self.__max_scores[week_num]

    def get_week_min(self, week_num):
        return self.__min_scores[week_num]

    def get_week_median(self, week_num):
        return self.__median_scores[week_num]

    def __weeks_to_calculate_vp(self):
        reg_season_count = self.__league.settings.reg_season_count
        league_current_week = self.__league.current_week
        print(f"reg_season_count: {reg_season_count}")
        print(f"league_current_week: {league_current_week}")
        if reg_season_count >= league_current_week:
            return league_current_week
        else:
            return reg_season_count + 1

    def calculate_victory_points(self):
        for cur_week in range(1, self.__weeks_to_calculate_vp()):
            self.__calculate_vp_for_week(cur_week)

    def __calculate_vp_for_week(self, week_num: int):
        box_scores = self.__league.box_scores(week_num)
        # Calculate the median_score and max_score for determining victory points
        week_scores = {}
        for matchup in box_scores:
            week_scores[matchup.home_team] = matchup.home_score
            week_scores[matchup.away_team] = matchup.away_score

        self.__median_scores[week_num] = median(week_scores.values())
        self.__max_scores[week_num] = max(week_scores.values())
        self.__min_scores[week_num] = min(week_scores.values())

        print(f"Week {week_num}; median: {self.__median_scores[week_num]} max: {self.__max_scores[week_num]}")

        for matchup in box_scores:
            if matchup.home_score >= matchup.away_score:
                # Home team won, ties go to the home team
                self.__all_teams[matchup.home_team.team_id].add_win(week_num, matchup.home_score)
                self.__all_teams[matchup.away_team.team_id].add_loss(week_num, matchup.away_score)
            else:
                # Away team won
                self.__all_teams[matchup.home_team.team_id].add_loss(week_num, matchup.home_score)
                self.__all_teams[matchup.away_team.team_id].add_win(week_num, matchup.away_score)

    def print_standings(self):
        df = self.__calculate_seeding()
        for d_id, d_name in self.__divisions.items():
            print()
            self.print_division_scores(df, d_id, d_name)
        print()
        self.print_weekly_victory_points(df)

    def __calculate_seeding(self):
        raw_data = list(map(lambda t: t.to_pandas_row(), self.__all_teams.values()))
        df = pd.DataFrame(raw_data)
        df["victory points"] = df["weekly_victory_points"].map(lambda x: sum(x.values()))
        df = df.sort_values(["victory points", "wins", "points for"],
                            ascending=(False, False, False))
        df["seed"] = np.arange(df.shape[0])
        df["seed"] = df["seed"] + 1
        df["record"] = df[["wins", "losses"]].apply(lambda x: '-'.join(x.astype(str)), axis=1)
        return df

    @staticmethod
    def print_division_scores(seeding_df, division_id, division_name):
        df = seeding_df[seeding_df["division_id"] == division_id]
        printable_df = df[["seed", "team", "record", "victory points", "points for"]]
        print("Division: {}".format(division_name))
        print(printable_df.to_string(index=False))

    @staticmethod
    def print_weekly_victory_points(seeding_df):
        def color_formatter(x):
            num = int(x)
            if num == 3:
                color = Colors.OKBLUE
            elif num == 2:
                color = Colors.OKGREEN
            elif num == 1:
                color = Colors.WARNING
            elif num == 0:
                color = Colors.FAIL
            else:
                color = Colors.FAIL
                # return "\U0001F4A9"

            return color + str(num) + Colors.ENDC

        df = seeding_df[["seed", "team", "weekly_victory_points"]]
        vpdf = seeding_df[["victory points"]]
        printable_df = pd.concat([df, df["weekly_victory_points"].apply(pd.Series), vpdf], axis=1) \
            .drop(columns="weekly_victory_points")

        formatters = {
            Team.week_to_str(1): color_formatter,
            Team.week_to_str(2): color_formatter,
            Team.week_to_str(3): color_formatter,
            Team.week_to_str(4): color_formatter,
            Team.week_to_str(5): color_formatter,
            Team.week_to_str(6): color_formatter,
            Team.week_to_str(7): color_formatter,
            Team.week_to_str(8): color_formatter,
            Team.week_to_str(9): color_formatter,
            Team.week_to_str(10): color_formatter,
            Team.week_to_str(11): color_formatter,
            Team.week_to_str(12): color_formatter,
            Team.week_to_str(13): color_formatter,
            Team.week_to_str(14): color_formatter,
        }

        print(printable_df.to_string(index=False, formatters=formatters))


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
