from steamroller.lib import config
import requests
from operator import itemgetter
from sys import exit
from random import SystemRandom
from steamroller.web import db
import models


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


class old_steam():
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


class Steam():
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

    def get_all_games(self):
        """
        Returns list of games owned by a Steam ID.
        """

        user = models.User.query.filter_by(steam_id=self.steam_id).one_or_none()
        games_query = models.Owned_Games.query.filter_by(user=user).all()

        games = []

        for game in games_query:
            games.append({'name': models.Game.query.get(game.game_id).title})

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
