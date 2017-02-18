#!/usr/bin/env python

import os
import sys
sys.path.append(os.path.abspath('bin'))

import config
import requests
from urllib import urlencode
import json
from operator import itemgetter
from random import SystemRandom

def main():
    games = get_games()
    
def get_games():
    params = {'key': config.get_steam_api_key(), 'steamid': config.get_steam_id(), 'include_appinfo': 1, 'format': 'json'}
    url = config.get_steam_api_url() + urlencode(params)
    r = requests.get(url)
    games = r.json()['response']['games']
    new_games = get_new_games(games)
    new_games = steam_sort(new_games)
    game_count = len(new_games)
    print 'Number of new games: ' + str(game_count)
    index_to_play = SystemRandom().randrange(game_count)
    print 'Game chosen is "' + new_games[index_to_play]['name'] + '"'

def get_new_games(games):
    # Gets the new games, those with 0 playtime.
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
    

if __name__ == "__main__":
    main()