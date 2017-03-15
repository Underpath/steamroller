from steamroller.web import app, oid, db
from steamroller.lib import config
from flask import render_template, request, flash, redirect, g, session, url_for
from steamroller.lib import games
from .forms import LoginForm
import re
from steamroller.web.models import User

@app.route('/')
@app.route('/index')
def index():
    user = {'steam_id': config.get_option('STEAM_ID')}
    return render_template('index.html', title='Home', user=user)

@app.route('/config')
def web_config():
    #return 'asdf'
    return  config.CONFIG_FILE
    #return config.get_option('STEAM_ID')

@app.route('/all')
def all_games():
    s = games.steam()
    user = {'steam_id': config.get_option('STEAM_ID')}
    return render_template('index.html', title='Home', user=user, games=s.games())

@app.route('/new')
def new_games():
    s = games.steam()
    user = {'steam_id': s.steam_id}
    return render_template('index.html', title='Home', user=user, games=s.new_games())

@app.route('/pick')
def pick():
    debug = request.args.get('debug')
    if debug == '1':
        debug = True
    else:
        debug = False
    s = games.steam()
    user = {'steam_id': s.steam_id}
    count, game = s.pick_new()
    game['early_access'] = games.is_early_access(game['appid'])
    game['PCGW_url'] = games.get_pcgw_url(game['appid'])
    print game
    return render_template('pick.html', title='Home', user=user, game=game, count=count, debug=debug)

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
    return oid.try_login('http://steamcommunity.com/openid')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(oid.get_next_url())

@oid.after_login
def create_or_login(resp):
    _steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')
    match = _steam_id_re.search(resp.identity_url)
    g.user = User.get_or_create(match.group(1))
    s = games.steam()
    steamdata = s.user_info()
    g.user.nickname = steamdata['personaname']
    db.session.commit()
    session['user_id'] = g.user.id
    flash('You are logged in as %s' % g.user.nickname)
    return redirect(oid.get_next_url())