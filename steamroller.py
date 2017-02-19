#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.abspath('lib'))

import config
import requests
from urllib import urlencode
import json
from operator import itemgetter
from random import SystemRandom
import argparse
import config_file

def main():
    usage()
    if not config_file.check_config_file(config.CONFIG_FILE):
        sys.exit()
    games = get_games()
    game_count = len(games)
    print 'Number of new games: ' + str(game_count)
    index_to_play = SystemRandom().randrange(game_count)
    print 'Game chosen is "' + games[index_to_play]['name'] + '"'
    
def get_games():
    # Returns sorted list of new games.
    params = {'key': config.get_steam_api_key(), 'steamid': config.get_steam_id(), 'include_appinfo': 1, 'format': 'json'}
    url = config.get_steam_api_url() + urlencode(params)
    r = requests.get(url)
    games = r.json()['response']['games']
    new_games = get_new_games(games)
    return steam_sort(new_games)

def get_new_games(games):
    # Returns a list of new games, those with 0 playtime.
    new_games = []
    exclusions = config.get_excluded_appids()
    inclusions = config.get_included_appids()
    for game in games:
        if game['appid'] in inclusions:
            new_games.append(game)
        elif game['playtime_forever'] == 0 and game['appid'] not in exclusions:
            new_games.append(game)

    return new_games

def steam_sort(games):
    # Sorts games so they appear in the same order as in Steam.
    determiners = config.get_steam_determiners()
    for game in games:
        sortname = game['name'].lower()
        for determiner in determiners:
            if sortname.lower().startswith(determiner + ' '):
                sortname = sortname.replace(determiner + ' ', '')
        sortname = sortname
        game['sortname'] = sortname
    return sorted(games, key=itemgetter('sortname'))


def usage():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', help="Show this help message and exit.", action='help')
    parser.add_argument('-g', '--config', help="Generate basic config file.", action='store_true')
    parser.add_argument('-w', '--config-wizard', help="Start wizard to build the config file.", action='store_true')
    args = parser.parse_args()
    if args.config:
        print 'generate config file'
        sys.exit()
    


if __name__ == "__main__":
    main()