import config
import config_file
from urlparse import urlparse
from urllib import urlencode
import requests
from operator import itemgetter
from sys import exit
from random import SystemRandom


def get_steamid(url):
    """
    Takes a Steamcommunity vanity URL and returns the Steam ID for that user.
    Uses a steam API for this.
    """

    config_file.check(config.CONFIG_FILE,
                      [config.get_default_option('API_KEY')])
    config_file.check(config.CONFIG_FILE,
                      [config.get_default_option('VANITY_URL_TO_STEAMID_API')])
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
        response = make_request_to_api(api_url, params)['response']
        if response['success'] == 1:
            return response['steamid']
        else:
            print 'Steam ID not found.'
            return False
    else:
        print "This doesn't look like a Steamcommunity URL, please try again."


def make_request_to_api(base_url, params=None):
    """
    Generic function to make HTTP requests, read the response as JSON and
    return the response as dictionary.
    """

    try:
        r = requests.get(base_url, params=params)
    except:
        print 'There was an error trying to reach the website.'
        exit()
    if r.status_code == 200:
        return r.json()


def steam_sort(games):
    """
    Takes a list of games and returns that list sorted in the same order as in
    Steam.
    """

    determiners = config.get_option('DETERMINERS', 'str_list')
    for game in games:
        sortname = game['name'].lower()
        for determiner in determiners:
            if sortname.lower().startswith(determiner + ' '):
                sortname = sortname.replace(determiner + ' ', '')
        sortname = sortname
        game['sortname'] = sortname
    return sorted(games, key=itemgetter('sortname'))


class steam():
    """
    Stores the steam_id for a user, has the functionality to get game related
    data for the steam_id.
    """

    def __init__(self, steam_id=config.get_option('STEAM_ID')):
        self.steam_id = steam_id

    def user_info(self):
        """
        Returns user info from a Steam ID.
        """

        params = {
            'key': config.get_option('API_KEY'),
            'steamids': self.steam_id
        }
        api_url = config.get_option('STEAM_USER_INFO_API')
        response = make_request_to_api(api_url, params)
        user_info = response['response']['players']['player'][0]
        return user_info

    def games(self):
        """
        Returns list of games owned by a Steam ID.
        """

        params = {'key': config.get_option('API_KEY'),
                  'steamid': config.get_option('STEAM_ID'),
                  'include_appinfo': 1,
                  'format': 'json'}
        games = make_request_to_api(config.get_option('OWNED_GAMES_API'),
                                    params)['response']['games']
        return steam_sort(games)

    def new_games(self):
        """
        Returns list of new games owned by a Steam ID. New games are those
        with 0 playtime and those included/excluded in options.
        """

        new_games = []
        exclusions = config.get_option('EXCLUDE', 'int_list')
        inclusions = config.get_option('INCLUDE', 'int_list')
        games = self.games()
        for game in games:
            if game['appid'] in inclusions:
                new_games.append(game)
            elif game['playtime_forever'] == 0 and \
                    game['appid'] not in exclusions:
                new_games.append(game)
        return steam_sort(new_games)

    def pick_new(self):
        """
        Returns game and details from the list of new games.
        """

        games = self.new_games()
        return pick_game(games)

    def pick_all(self):
        """
        Returns game and details from the list of all games.
        """

        games = self.games()
        return pick_game(games)


def is_early_access(appid):
    """
    Queries the steam API for the game genres and returns true if 'Early
    Access' is among them.
    """

    api_url = config.get_option('STEAMAPP_DETAILS_API')
    params = {'appids': appid}
    app_data = make_request_to_api(api_url, params)
    genres = app_data[str(appid)]['data']['genres']
    for genre in genres:
        if int(genre['id']) == 70:
            return True
    return False


def pick_game(games):
    """
    Returns count of games on a list, and one of those games picked at random.
    """
    count = len(games)
    pick = SystemRandom().randrange(count)
    return count, games[pick]


def get_pcgw_url(appid):
    """
    Returns the URL for the game in PCGamingWiki or false if not found.
    """

    params = {'action': 'askargs', 'format': 'json',
              'conditions': 'Steam AppID::' + str(appid)}
    api_url = config.get_option('PCGW_API')
    url = make_request_to_api(api_url, params)['query']
    if url['results']:
        url = url['results'].values()[0]['fullurl']
        return url
    return False
