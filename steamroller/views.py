from steamroller import app, oid, db
from flask import render_template, request, flash, redirect, g, session, \
    url_for, abort
from functools import wraps
import games
import util
import re
from models import User
from urlparse import urlparse, parse_qs, urljoin


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None and request.path.lower() == '/logout':
            return redirect(url_for('index'))
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
    my_page = {}
    my_page['title'] = 'About'
    my_page['location'] = 'about'
    return render_template('about.html', my_page=my_page, user=user)


@app.route('/all/', defaults={'section': 1})
@app.route('/all/<int:section>')
@login_required
def all_games(section):
    user = get_user_details()
    s = games.Steam(user['steam_id'])
    my_page = {}
    my_page['title'] = 'All Games'
    my_page['location'] = 'all'
    all_my_games = s.get_all_games()
    app.logger.debug('Listing games in page {} for user "{}" from all.'.format(str(section), user['steam_id']), extra=games.get_log_data())
    return generate_list_view(all_my_games, user, my_page, section)


@app.route('/new/', defaults={'section': 1})
@app.route('/new/<int:section>')
@login_required
def new_games(section):
    user = get_user_details()
    s = games.Steam(user['steam_id'])
    my_page = {}
    my_page['title'] = 'New Games'
    my_page['location'] = 'new'
    s = games.Steam(user['steam_id'])
    my_new_games = s.new_games()
    app.logger.debug('Listing games in page {} for user "{}" from new.'.format(str(section), user['steam_id']), extra=games.get_log_data())
    return generate_list_view(my_new_games, user, my_page, section)


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
    my_page = {}
    my_page['title'] = 'Pick game'
    my_page['location'] = 'pick'
    picks = s.pick_new()

    if picks:
        count, game = picks
        app.logger.debug('Picked game {{id: {}, steam_appid: {}}} for user "{}".'.format(str(game['id']), str(game['appid']), user['steam_id']), extra=games.get_log_data())
        return render_template('pick.html', my_page=my_page, user=user,
                               game=game, count=count, debug=debug)
    else:
        app.logger.error('Error picking game for user "{}".'.format(user['steam_id']), extra=games.get_log_data())
        return render_template('error.html', my_page=my_page, user=user)


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
    user = get_user_details()
    my_page = {}
    my_page['title'] = ''
    my_page['location'] = ''
    if not operation or not game_id:
        app.logger.error('Error while executing operation "{}" with game_id: {} for user "{}": Not enough parameters.'.format(operation, str(game_id), user['steam_id']), extra=games.get_log_data())
        return render_template('error.html', my_page=my_page, user=user)
    if operation == 'Add':
        flash('Added "{}" to new games.'.format(game_name.encode('utf-8')), 'blue')
    elif operation == 'Remove':
        flash('Removed "{}" from new games.'.format(game_name.encode('utf-8')), 'blue')
    app.logger.debug('Executing operation "{}" with game_id: {} for user "{}".'.format(operation, str(game_id), user['steam_id']), extra=games.get_log_data())
    games.change_game_preference(user['steam_id'], game_id, operation)
    return redirect(request.referrer)


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
    app.logger.debug('Starting authentication process.', extra=games.get_log_data())
    return oid.try_login('https://steamcommunity.com/openid')


@app.route('/logout')
@login_required
def logout():
    app.logger.debug('Terminating session for user "{}".'.format(g.user.steam_id), extra=games.get_log_data())
    session.pop('user_id', None)
    flash('You have been logged out', 'green')
    return redirect(url_for('index'))


@app.route('/health')
def health_check():
    return 'Healthy'


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

    app.logger.info('User "{}" authenticated.'.format(g.user.steam_id), extra=games.get_log_data())
    return redirect(next_url)


@app.errorhandler(404)
def page_not_found(e):
    my_page = {}
    my_page['title'] = '404 - Error'
    my_page['location'] = '404'
    user = get_user_details()
    return render_template('404.html', my_page=my_page, user=user), 404


def get_user_details():
    user = {}
    if g.user:
        user['steam_id'] = g.user.steam_id
        user['nickname'] = g.user.nickname
        user['avatar_url'] = g.user.avatar_url
    return user


def generate_list_view(my_games, user, page_details, section):
    """
    Renders the list of the provided games after pagination or an error if
    something goes wrong.
    """

    if my_games:
        pagination = util.paginate(section, my_games)
        if pagination and section > 0:
            return render_template('list_games.html', my_page=page_details,
                                   user=user, pagination=pagination)
        else:
            abort(404)
    else:
        app.logger.error('Error while getting games for user "{}".'.format(user['steam_id']), extra=games.get_log_data())
        return render_template('error.html', my_page=page_details, user=user)


@app.endpoint('static')
def static(filename):
    static_url = app.config.get('STATIC_URL')

    if static_url:
        return redirect(urljoin(static_url, filename))

    return app.send_static_file(filename)
