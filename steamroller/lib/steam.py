import config
import config_file
from urlparse import urlparse
from urllib import urlencode
import requests
from operator import itemgetter
from sys import exit


def get_steamid(url):
    """Takes a Steamcommunity vanity URL and returns the Steam ID for that
    user. Uses a steam API for this."""
    config_file.check_config_file(config.CONFIG_FILE,
                                  [config.get_default_option('API_KEY')])
    config_file.check_config_file(config.CONFIG_FILE,
                                  [config.get_default_option('VANITY_URL_TO_' +
                                                             'STEAMID_API')])
    parsed_url = urlparse(url)
    parsed_steam_url = urlparse(config.get_option('STEAMCOMMUNITY_BASE_URL'))
    url_path = parsed_url.path.split('/')
    steam_url_path = parsed_steam_url.path.replace('/', '')
    is_steam_url = True

    # Checks to make sure Steamcommunity URL is good.
    if parsed_url.netloc != parsed_steam_url.netloc:
        is_steam_url = False
    elif len(url_path) != 3:
        is_steam_url = False
    elif url_path[1] != steam_url_path:
        is_steam_url = False
    elif not url_path[2]:
        is_steam_url = False

    if is_steam_url:
        params = {'key': config.get_option('API_KEY'),
                  'vanityurl': url_path[2], 'format': 'json'}
        api_url = config.get_option('VANITY_URL_TO_STEAMID_API')
        response = make_request_to_api(api_url, params)
        if response['success'] == 1:
            return response['steamid']
        else:
            print 'Steam ID not found.'
            return False
    else:
        print "This doesn't look like a Steamcommunity URL, please try again."


def make_request_to_api(base_url, params=None):
    """Generic function to make HTTP requests, read the response as JSON and
    return the response as dictionary."""
    if params:
        url = base_url + urlencode(params)
    else:
        url = base_url

    try:
        r = requests.get(url)
    except:
        print 'There was an error trying to reach the website.'
        exit()
    if r.status_code == 200:
        return r.json()['response']


def get_games():
    """Returns list of owned games for a SteamID."""
    params = {'key': config.get_option('API_KEY'),
              'steamid': config.get_option('STEAM_ID'), 'include_appinfo': 1,
              'format': 'json'}
    games = make_request_to_api(config.get_option('OWNED_GAMES_API'),
                                params)['games']
    return games


def get_new_games(games):
    """Takes a list of games and returns a list of games that are new, those
    with 0 playtime taking the 'INCLUDE' and 'EXCLUDE' options into account."""
    new_games = []
    exclusions = config.get_option('EXCLUDE', 'int_list')
    inclusions = config.get_option('INCLUDE', 'int_list')
    for game in games:
        if game['appid'] in inclusions:
            new_games.append(game)
        elif game['playtime_forever'] == 0 and game['appid'] not in exclusions:
            new_games.append(game)
    return new_games


def steam_sort(games):
    """Takes a list of games and returns that list sorted in the same order as
    in Steam."""
    determiners = config.get_option('DETERMINERS', 'str_list')
    for game in games:
        sortname = game['name'].lower()
        for determiner in determiners:
            if sortname.lower().startswith(determiner + ' '):
                sortname = sortname.replace(determiner + ' ', '')
        sortname = sortname
        game['sortname'] = sortname
    return sorted(games, key=itemgetter('sortname'))
