from steamroller.web import app, oid, db
from steamroller.lib import config
from flask import render_template, request, flash, redirect, g, session, \
    url_for
from functools import wraps
from steamroller.lib import games as old_games
import games
import re
from steamroller.web.models import User
from urlparse import urlparse, parse_qs


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('You are not logged in')
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/index')
def index():
    if g.user:
        user = {'nickname': g.user.nickname}
    else:
        user = {'nickname': 'None'}
    page = {}
    page['title'] = 'Home'
    page['location'] = 'home'
    return render_template('base.html', page=page, user=user)


@app.route('/config')
def web_config():
    return config.CONFIG_FILE


@app.route('/old_all')
@login_required
def old_all_games():
    user = {}
    user['steam_id'] = g.user.steam_id
    user['nickname'] = g.user.nickname
    s = old_games.steam(user['steam_id'])
    page = {}
    page['title'] = 'All Games'
    page['location'] = 'all'
    return render_template('list_games.html', page=page, user=user,
                           games=s.games())


@app.route('/all')
@login_required
def all_games():
    user = {}
    user['steam_id'] = g.user.steam_id
    user['nickname'] = g.user.nickname
    s = games.Steam(user['steam_id'])
    page = {}
    page['title'] = 'All Games'
    page['location'] = 'all'
    all_games = s.get_all_games()
    return render_template('list_games.html', page=page, user=user,
                           games=all_games)


@app.route('/new')
@login_required
def new_games():
    user = {}
    user['steam_id'] = g.user.steam_id
    user['nickname'] = g.user.nickname
    s = games.Steam(user['steam_id'])
    page = {}
    page['title'] = 'New Games'
    page['location'] = 'new'

    s = games.Steam(user['steam_id'])

    return render_template('list_games.html', page=page, user=user,
                           games=s.new_games())


@app.route('/pick')
@login_required
def pick():
    debug = request.args.get('debug')
    if debug == '1':
        debug = True
    else:
        debug = False
    user = {}
    user['steam_id'] = g.user.steam_id
    user['nickname'] = g.user.nickname
    print "\n\n\n" + g.user.avatar_url + "\n\n\n"
    user['avatar_url'] = g.user.avatar_url
    s = games.Steam(user['steam_id'])
    # KeyError: 'genres' when picking http://store.steampowered.com/api/appdetails?appids=542974
    count, game = s.pick_new()
    page = {}
    page['title'] = 'Pick game'
    page['location'] = 'pick'
    return render_template('pick.html', page=page, user=user, game=game,
                           count=count, debug=debug)


@app.route('/change_game_preference', methods=['POST'])
@login_required
def change_game_preference():
    """
    Takes a game ID through a post request and removes it from the elegible
    games pool.
    """
    #game_id = request.args.post('game_id', '', int)
    #operation = request.args.post('operation', '', str)
    game_id = request.form['game_id']
    operation = request.form['operation']
    print game_id
    print operation
    if not operation or not game_id:
        print "Not enough parameters."
        return "ERROR"
    games.change_game_preference(g.user.steam_id, game_id, operation)
    return redirect(request.referrer)


@app.route('/base')
def base():
    user = {}
    user['steam_id'] = 3
    user['nickname'] = 'god'
    page = {}
    page['title'] = 'Base'
    page['location'] = 'base'
    return render_template('base.html', page=page, user=user)


@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@app.route('/login')
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('index'))
    return oid.try_login('https://steamcommunity.com/openid')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(url_for('index'))


@oid.after_login
def create_or_login(resp):
    _steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')
    steam_id = _steam_id_re.search(resp.identity_url).group(1)
    s = games.Steam(steam_id)
    steamdata = s.user_info()
    nickname = steamdata['personaname']
    avatar_url = steamdata['avatar']
    g.user = User.get_or_create(steam_id, nickname, avatar_url)
    db.session.commit()
    session['user_id'] = g.user.id
    session['nickname'] = g.user.nickname
    session['avatar_url'] = g.user.avatar_url
    flash('You are logged in as %s' % g.user.nickname)
    params = parse_qs(urlparse(request.args.get('next')).query)
    if 'next' in params:
        next_url = urlparse(params['next'][0]).path
    else:
        next_url = oid.get_next_url()
    return redirect(next_url)
