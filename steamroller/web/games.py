from steamroller.lib import config
import requests
from operator import itemgetter
from random import SystemRandom
from steamroller.web import db
import models
from datetime import datetime
from sqlalchemy import or_


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
        Queries the steam API using the steam ID and returns user info.
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
        update = trigger_update(user)
        if update == 2:
            return False

        games_query = models.Owned_Games.query.filter_by(user=user).all()
        games = result_to_dict(games_query)
        for game in games:
            game['appid'] = get_app_id(game['id'])
        return games

    def new_games(self):
        """
        Returns list of new games owned by a Steam ID. New games are those
        with 0 playtime and those included/excluded in options.
        """

        user = self.user

        update = trigger_update(user)
        if update == 2:
            return False

        games_query = models.Owned_Games.query

        games_query = games_query.filter(models.Owned_Games.user == user,
                                         models.Owned_Games.exclude == False,
                                         or_(models.Owned_Games.include == True,
                                             models.Owned_Games.is_new == True))
        games_query = games_query.all()
        new_games = result_to_dict(games_query)

        for game in new_games:
            game['appid'] = get_app_id(game['id'])
        return new_games

    def pick_new(self):
        """
        Returns game and details from the list of new games.
        """

        games = self.new_games()
        if not games:
            return False
        count, game = pick_game(games)
        game['PCGW_url'] = get_pcgw_url(game['id'])
        game['appid'] = get_app_id(game['id'])
        return count, game

    def pick_all(self):
        """
        Returns game and details from the list of all games.
        """

        games = self.games()
        return pick_game(games)


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


def is_early_access(game_id):
    """
    Queries the steam API for the game's genres and returns true if 'Early
    Access' is among them.
    """

    game = models.Game.query.get(game_id)
    if game.is_early_access is None or game.is_early_access == True:
        if game.last_checked:
            time_since_update = datetime.now() - game.last_checked
            threshold = int(config.get_option('GAME_REFRESH_TIME'))
            if time_since_update.total_seconds() < threshold:
                print "Game updated recently, returning value from DB."
                return bool(game.is_early_access)

        print "Checking early access status on Steam."
        api_url = config.get_option('STEAMAPP_DETAILS_API')
        appid = game.games_in_store[0].game_store_id
        params = {'appids': appid}
        app_data = make_request_to_api(api_url, params)
        if not app_data:
            return False
        for key in app_data:
            if app_data[key]['success'] is False:
                print "Request to API returned unsuccesful."
                return False
            if 'genres' not in app_data[str(appid)]['data']:
                return False

            genres = app_data[str(appid)]['data']['genres']
            game.last_checked = datetime.now()
            for genre in genres:
                if int(genre['id']) == 70:
                    game.is_early_access = True
                    db.session.add(game)
                    db.session.commit()
                    return bool(game.is_early_access)
            game.is_early_access = False
            db.session.add(game)
            db.session.commit()
            return bool(game.is_early_access)
        return False
    else:
        print "Not early access according to the DB."
        return False


def pick_game(games):
    """
    Returns count of games on a list, and one of those games picked at random.
    """

    count = len(games)
    pick = SystemRandom().randrange(count)
    print "Game picked:"
    print games[pick]
    games[pick]['is_early_access'] = is_early_access(games[pick]['id'])
    return count, games[pick]


def get_app_id(game_id):
    """
    Given one local game_id, return the corresponding steam appid.
    """

    game = models.Game.query.get(game_id)
    return game.games_in_store[0].game_store_id


def get_pcgw_url(game_id):
    """
    Returns the URL for the game in PCGamingWiki or False if not found.
    """
    appid = get_app_id(game_id)

    params = {'action': 'askargs', 'format': 'json',
              'conditions': 'Steam AppID::' + str(appid)}
    api_url = config.get_option('PCGW_API')
    url = make_request_to_api(api_url, params)
    if url:
        url = url['query']
        if url['results']:
            url = url['results'].values()[0]['fullurl']
            return url
    return False


def make_request_to_api(base_url, params=None):
    """
    Generic function to make HTTP requests, read the response as JSON and
    return the response as dictionary. If the request fails returns False.
    """

    print "Making request to: " + base_url
    print "\tParams: " + str(params)
    try:
        r = requests.get(base_url, params=params)
        print "Request made to: " + r.url
    except:
        print 'There was an error trying to reach the website.'
        return False
    if r.status_code == 200:
        response = r.json()
        return response
    else:
        print "API request returned non 200 status code:\n\tURL: " + r.url + \
            "Status code: " + str(r.status_code)
    return False


def trigger_update(user):
    """
    Takes a user object from the models and returns whether games associated
    with it need to be updated based on the time threshold defined in the
    configuration. Responses are as follows:
        0: Games were updated.
        1: Games are to be fetched from the local DB.
        2: Error making API request to update the games.
    """

    if user.games_updated:
        time_since_update = datetime.now() - user.games_updated
        threshold = int(config.get_option('USER_REFRESH_TIME'))
        if time_since_update.total_seconds() < threshold:
            print "Fetching games from local DB."
            #return 1
    print "Updating games for user."

    if not update_games_for_user(user):
        print 'not update_games_for_user'
        return 2
    return 0


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
                                params)
    if not games:
        return False
    games = games['response']['games']
    # {u'playtime_forever': 12, u'name': u'Zombie Shooter',
    # u'img_logo_url': u'2e4082032b2a7e8b1782fc7515fcf5c4056d5050',
    # u'appid': 33130,
    # u'img_icon_url': u'db67664d7085947dd8d7dd74739230d9a09be5c7',
    # 'sortname': u'zombie shooter'}
    user.games_updated = datetime.now()

    store = models.Store.query.filter_by(name='Steam').one_or_none()
    records = []
    with db.session.no_autoflush:
        for game in games:
            game_obj = models.Game.query.filter_by(name=game['name'])
            game_obj = game_obj.one_or_none()
            if not game_obj:
                game_obj = models.Game(game['name'], game['img_logo_url'])
                records.append(game_obj)
                game_in_store = models.Games_in_Store(store=store,
                                                      game=game_obj,
                                                      game_store_id=game['appid'])
                records.append(game_in_store)

            game_owned = models.Owned_Games.query.filter_by(game=game_obj,
                                                            user=user)
            game_owned = game_owned.one_or_none()

            if game['playtime_forever'] == 0:
                is_new = True
            else:
                is_new = False

            if game_owned:
                if game_owned.is_new is not is_new:
                    game_owned.is_new = is_new
                    records.append(game_owned)
            else:
                records.append(models.Owned_Games(user=user, game=game_obj,
                                                  is_new=is_new))
    db.session.add_all(records)
    db.session.commit()
    return True


def result_to_dict(games_query):
    games = []
    for game in games_query:
        game_obj = models.Game.query.get(game.game_id)
        game_details = game_obj.__dict__
        game_details.pop('_sa_instance_state', None)
        if game.exclude is False and (game.include is True or game.is_new is
                                      True):
            game_details['is_new'] = True
        else:
            game_details['is_new'] = False
        games.append(game_details)
    return steam_sort(games)


def change_game_preference(steam_id, game_id, operation):
    """
    Function to change whether a game should be included or excluded when
    listing new games for a user.
    """
    user = models.User.query.filter_by(steam_id=steam_id).one_or_none()
    owned_game_obj = models.Owned_Games.query.filter_by(game_id=game_id, user=user).one_or_none()

    if not owned_game_obj:
        print "Seems user " + str(user.id) + "does not own game " + str(game_id)

    if operation == 'Remove' and owned_game_obj.exclude is False:
        owned_game_obj.exclude = True
        owned_game_obj.include = False
        print "Excluding game " + str(game_id) + " for user " + str(user.id)
    elif operation == 'Add' and owned_game_obj.include is False:
        owned_game_obj.exclude = False
        owned_game_obj.include = True
        is_early_access(game_id)
        print "Including game " + str(game_id) + " for user " + str(user.id)
    else:
        print "Game already excluded."
    db.session.add(owned_game_obj)
    db.session.commit()
