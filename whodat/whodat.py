import configparser
import operator
from collections import defaultdict
from statistics import median

from espn_api.football import League

league_year = 2021


def read_config():
    config = configparser.ConfigParser()
    config.read('secrets.conf')
    return {
        'espn_league_id': int(config['DEFAULT']['espn_league_id']),
        'espn_s2': config['DEFAULT']['espn_s2'],
        'swid': config['DEFAULT']['swid']
    }


def build_division_map(league: League):
    divisions = defaultdict(list)
    for team in league.teams:
        divisions[team.division_name].append(team)

    return divisions


def print_standings(divisions, victory_points):
    sorted_vp = dict(sorted(victory_points.items(), key=lambda item: item[1]))
    for division, teams in divisions.items():
        print("")
        print("Division {}".format(division))
        div_vps = {team_id: sorted_vp[team_id] for team_id in map(lambda x: x.team_id, teams)}
        sorted_div_vps = dict(sorted(div_vps.items(), key=operator.itemgetter(1), reverse=True))
        for team_id, vp in sorted_div_vps.items():
            team = next(x for x in teams if x.team_id == team_id)
            print("{} {}-{}\t{}".format(team.team_name,
                                        team.wins,
                                        team.losses,
                                        vp))


def calculate_points_for_week(league: League, week_num, victory_points):
    box_scores = league.box_scores(week_num)
    week_scores = {}
    for matchup in box_scores:
        week_scores[matchup.home_team] = matchup.home_score
        week_scores[matchup.away_team] = matchup.away_score

    median_score = median(week_scores.values())
    max_score = max(week_scores.values())
    print('The median score for week {} was {}'.format(week_num, median_score))
    for matchup in box_scores:
        if matchup.home_score >= matchup.away_score:
            victory_points[matchup.home_team.team_id] = victory_points[
                                                            matchup.home_team.team_id] + 2
            if matchup.away_score > median_score:
                victory_points[matchup.away_team.team_id] = victory_points[
                                                                matchup.away_team.team_id] + 1
            if matchup.home_score == max_score:
                victory_points[matchup.home_team.team_id] = victory_points[
                                                                matchup.home_team.team_id] + 1
        else:
            victory_points[matchup.away_team.team_id] = victory_points[
                                                            matchup.away_team.team_id] + 2
            if matchup.home_score > median_score:
                victory_points[matchup.home_team.team_id] = victory_points[
                                                                matchup.home_team.team_id] + 1
            if matchup.away_score == max_score:
                victory_points[matchup.away_team.team_id] = victory_points[
                                                                matchup.away_team.team_id] + 1


if __name__ == '__main__':
    conf = read_config()

    __league = League(league_id=conf['espn_league_id'],
                      year=league_year,
                      espn_s2=conf['espn_s2'],
                      swid=conf['swid'])

    # initialize victory points
    __victory_points = {}
    for t in __league.teams:
        __victory_points[t.team_id] = 0

    __divisions = build_division_map(__league)

    reg_season_week = None
    if __league.settings.reg_season_count > __league.current_week:
        reg_season_week = __league.current_week
    else:
        reg_season_week = __league.settings.reg_season_count

    for cur_week in range(1, reg_season_week):
        calculate_points_for_week(__league, cur_week, __victory_points)

    print_standings(__divisions, __victory_points)
