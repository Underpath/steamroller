from steamroller.lib import config
import requests
from operator import itemgetter
from sys import exit
from random import SystemRandom
from steamroller.web import db
import models
from datetime import datetime
from sqlalchemy import or_


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
        self.user = models.User.query.filter_by(steam_id=steam_id)
        self.user = self.user.one_or_none()

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

        user = self.user
        trigger_update(user)

        games_query = models.Owned_Games.query.filter_by(user=user).all()

        return result_to_dict(games_query)


    def new_games(self):
        """
        Returns list of new games owned by a Steam ID. New games are those
        with 0 playtime and those included/excluded in options.
        """

        user = self.user
        trigger_update(user)

        games_query = models.Owned_Games.query.filter(models.Owned_Games.user == user, models.Owned_Games.exclude == False, or_(models.Owned_Games.include == True, models.Owned_Games.is_new == True)).all()

        return result_to_dict(games_query)

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

def trigger_update(user):
    """
    Takes a user object from the models and returns whether games associated
    with it need to be updated based on the time threshold defined in the
    configuration.
    """

    if user.games_updated:
        time_since_update = datetime.now() - user.games_updated
        threshold = int(config.get_option('USER_REFRESH_TIME'))
        if time_since_update.total_seconds() < threshold:
            print "Fetching games from local DB."
            return False
    print "Updating games for user."
    update_games_for_user(user)
    return True

def update_games_for_user(user):
    """
    Takes a list of games and a user object from the models and updates games
    owned by that user, also adding any games that might be missing from the
    DB.
    """

    params = {'key': config.get_option('API_KEY'),
              'steamid': user.steam_id,
              'include_appinfo': 1, 'format': 'json'}
    games = make_request_to_api(config.get_option('OWNED_GAMES_API'),
                                params)['response']['games']
    # {u'playtime_forever': 12, u'name': u'Zombie Shooter', u'img_logo_url': u'2e4082032b2a7e8b1782fc7515fcf5c4056d5050', u'appid': 33130, u'img_icon_url': u'db67664d7085947dd8d7dd74739230d9a09be5c7', 'sortname': u'zombie shooter'}
    user.games_updated = datetime.now()

    store = models.Store.query.filter_by(name='Steam').one_or_none()
    records = []
    with db.session.no_autoflush:
        for game in games:
            game_obj = models.Game.query.filter_by(name=game['name']).one_or_none()
            if not game_obj:
                game_obj = models.Game(game['name'])
                records.append(game_obj)
                game_in_store = models.Games_in_Store(store=store, game=game_obj, game_store_id=game['appid'])
                records.append(game_in_store)

            game_owned = models.Owned_Games.query.filter_by(game=game_obj,user=user).one_or_none()

            if game['playtime_forever'] == 0:
                is_new = True
            else:
                is_new = False

            if game_owned:
                if game_owned.is_new is not is_new:
                    game_owned.is_new = is_new
                    records.append(game_owned)
            else:
                records.append(models.Owned_Games(user=user, game=game_obj, is_new=is_new))
    db.session.add_all(records)
    db.session.commit()

def result_to_dict(games_query):
    games = []
    for game in games_query:
        game_obj = models.Game.query.get(game.game_id)
        game_details = game_obj.__dict__
        game_details.pop('_sa_instance_state', None)
        games.append(game_details)
    return steam_sort(games)