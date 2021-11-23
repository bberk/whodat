import configparser

from espn_api.football import League as EspnLeague

from league import League


league_year = 2021


def read_config():
    config = configparser.ConfigParser()
    config.read('secrets.conf')
    return {
        'espn_league_id': int(config['DEFAULT']['espn_league_id']),
        'espn_s2': config['DEFAULT']['espn_s2'],
        'swid': config['DEFAULT']['swid']
    }


if __name__ == '__main__':
    conf = read_config()

    espn_league = EspnLeague(league_id=conf['espn_league_id'],
                             year=league_year,
                             espn_s2=conf['espn_s2'],
                             swid=conf['swid'])

    __league = League(espn_league)

    __league.calculate_victory_points()

    __league.print_standings()
