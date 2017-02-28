#!/usr/bin/env python

from lib import config
from lib import config_file
from lib import steam
import argparse
import os
import sys

config_file_path = config.CONFIG_FILE


def main(param):
    config_file.check(config_file_path)
    s = steam.steam()
    if param == 'all':
        game_count, game = s.pick_all()
        output = "Total number of games: "
    else:
        game_count, game = s.pick_new()
        output = "New games to choose from: "
    print output + str(game_count)
    print 'Game chosen is "' + game['name'] + '"'


def print_list(filtered='new'):
    """Prints games to screen, depending on the 'filtered' parameter prints all
    or only new ones."""

    s = steam.steam()
    if filtered == 'new':
        games = s.new_games()
    elif filtered == 'all':
        games = s.games()
    for game in games:
        print str(game['appid']) + ' - ' + game['name']


def usage():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-a', '--all', help="Choose from all games.",
                        action='store_true')
    parser.add_argument('-g', '--config', help="Generate basic config file.",
                        action='store_true')
    parser.add_argument('-h', '--help',
                        help="Show this help message and exit.", action='help')
    parser.add_argument('-i', '--list-all',
                        help="List all games with their appid.",
                        action='store_true')
    parser.add_argument('-l', '--list',
                        help="List new games with their appid.",
                        action='store_true')
    parser.add_argument('-s', '--steam-id',
                        metavar='http://steamcommunity.com/id/<username>',
                        help="Returns the steam ID for the user of a given " +
                        "steamcommunity URL.", type=str)
    args = parser.parse_args()

    if args.config:
        print "Generating config file..."
        config_file.generate_basic_config(config_file_path)
        sys.exit()
    elif args.steam_id:
        steam_id = steam.get_steamid(args.steam_id)
        if steam_id:
            print 'Steam ID: ' + steam_id
        sys.exit()
    elif args.list:
        print_list()
        sys.exit()
    elif args.list_all:
        print_list('all')
        sys.exit()
    elif args.all:
        return 'all'


if __name__ == "__main__":
    param = usage()
    main(param)
