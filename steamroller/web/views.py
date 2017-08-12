from steamroller.web import app, oid, db
from flask import render_template, request, flash, redirect, g, session, \
    url_for, abort
from functools import wraps
import games
import util
import re
from steamroller.web.models import User
from urlparse import urlparse, parse_qs


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            flash('You should log in before trying that', 'red')
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
@app.route('/index')
def index():
    if g.user:
        user = get_user_details()
    else:
        user = None
    page = {}
    page['title'] = 'About'
    page['location'] = 'about'
    return render_template('base.html', page=page, user=user)


@app.route('/all')
@login_required
def all_games():
    user = get_user_details()
    s = games.Steam(user['steam_id'])
    page = {}
    page['title'] = 'All Games'
    page['location'] = 'all'
    all_my_games = s.get_all_games()
    if all_my_games:
        return render_template('list_games.html', page=page, user=user,
                               games=all_my_games)
    else:
        return render_template('error.html', page=page, user=user)


@app.route('/all2/', defaults={'section': 1})
@app.route('/all2/<int:section>')
@login_required
def all_games2(section):
    user = get_user_details()
    s = games.Steam(user['steam_id'])
    my_page = {}
    my_page['title'] = 'All Games'
    my_page['location'] = 'all2'
    all_my_games = s.get_all_games()
    if all_my_games:
        pagination = util.paginate(section, all_my_games)
        if pagination and section > 0:
            return render_template('list_games2.html', page=my_page, user=user,
                                pagination=pagination)
        else:
            abort(404)
    else:
        return render_template('error.html', page=my_page, user=user)


@app.route('/new')
@login_required
def new_games():
    user = get_user_details()
    s = games.Steam(user['steam_id'])
    page = {}
    page['title'] = 'New Games'
    page['location'] = 'new'

    s = games.Steam(user['steam_id'])
    my_new_games = s.new_games()

    if my_new_games:
        return render_template('list_games.html', page=page, user=user,
                               games=my_new_games)
    else:
        return render_template('error.html', page=page, user=user)


@app.route('/pick')
@login_required
def pick():
    debug = request.args.get('debug')
    if debug == '1':
        debug = True
    else:
        debug = False
    user = get_user_details()
    s = games.Steam(user['steam_id'])
    page = {}
    page['title'] = 'Pick game'
    page['location'] = 'pick'
    picks = s.pick_new()
    if picks:
        count, game = picks
        return render_template('pick.html', page=page, user=user, game=game,
                               count=count, debug=debug)
    else:
        return render_template('error.html', page=page, user=user)


@app.route('/change_game_preference', methods=['POST'])
@login_required
def change_game_preference():
    """
    Takes a game ID through a post request and removes/adds it from the
    elegible games pool.
    """
    game_id = request.form['game_id']
    game_name = request.form['game_name']
    operation = request.form['operation']
    print game_id
    print operation
    if not operation or not game_id:
        print "Not enough parameters."
        return "ERROR"
    if operation == 'Add':
        flash('Added "' + game_name + '" to new games.', 'blue')
    elif operation == 'Remove':
        flash('Removed "' + game_name + '" from new games.', 'blue')
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
    flash('You have been logged out', 'green')
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
    flash('You are logged in as %s' % g.user.nickname, 'green')
    params = parse_qs(urlparse(request.args.get('next')).query)
    if 'next' in params:
        next_url = urlparse(params['next'][0]).path
    else:
        next_url = oid.get_next_url()
    return redirect(next_url)

@app.errorhandler(404)
def page_not_found(e):
    #return render_template('404.html'), 404
    return "error 404"

def get_user_details():
    user = {}
    user['steam_id'] = g.user.steam_id
    user['nickname'] = g.user.nickname
    user['avatar_url'] = g.user.avatar_url
    return user
