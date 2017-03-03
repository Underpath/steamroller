from steamroller.web import app
from steamroller.lib import config
from flask import render_template, request
from steamroller.lib import steam

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
    s = steam.steam()
    user = {'steam_id': config.get_option('STEAM_ID')}
    return render_template('index.html', title='Home', user=user, games=s.games())

@app.route('/new')
def new_games():
    s = steam.steam()
    user = {'steam_id': s.steam_id}
    return render_template('index.html', title='Home', user=user, games=s.new_games())

@app.route('/pick')
def pick():
    debug = request.args.get('debug')
    if debug == '1':
        debug = True
    else:
        debug = False
    print debug
    s = steam.steam()
    user = {'steam_id': s.steam_id}
    count, game = s.pick_new()
    early_access = steam.is_early_access(game['appid'])
    
    return render_template('pick.html', title='Home', user=user, game=game, count=count, debug=debug, early_access=early_access)