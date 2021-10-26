from statistics import median

import numpy as np
import pandas as pd
from espn_api.football import League as EspnLeague

from team import Team


class League:

    def __init__(self, espn_league: EspnLeague):
        self.__league = espn_league
        self.__divisions = {}  # dict of division_id -> division_name
        self.__all_teams = {}  # dict of team_id -> Team
        self.__median_scores = {}  # dict of week_num -> median_score
        self.__max_scores = {}  # dict of week_num -> max_score
        self.__build_teams()
        self.__build_divisions()

    def __build_teams(self):
        for espnTeam in self.__league.teams:
            team = Team(espnTeam, self)
            self.__all_teams[espnTeam.team_id] = team

    def __build_divisions(self):
        for team in self.__all_teams.values():
            self.__divisions[team.get_division_id()] = team.get_division_name()

    def get_week_max(self, week_num):
        return self.__max_scores[week_num]

    def get_week_median(self, week_num):
        return self.__median_scores[week_num]

    def __weeks_to_calculate_vp(self):
        reg_season_count = self.__league.settings.reg_season_count
        league_current_week = self.__league.current_week
        if reg_season_count > league_current_week:
            return league_current_week
        else:
            return reg_season_count

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
        df = seeding_df[["seed", "team", "weekly_victory_points"]]
        printable_df = pd.concat([df, df["weekly_victory_points"].apply(pd.Series)], axis=1)\
            .drop(columns="weekly_victory_points")
        print(printable_df.to_string(index=False))
