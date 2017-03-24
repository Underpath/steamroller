from steamroller.web import db
from sqlalchemy import Integer


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String(40), unique=True)
    nickname = db.Column(db.String(80))
    games_updated = db.Column(db.DateTime)

    @staticmethod
    def get_or_create(steam_id, nickname):
        rv = User.query.filter_by(steam_id=steam_id).first()
        if rv is None:
            rv = User()
            rv.steam_id = steam_id
            rv.nickname = nickname
            db.session.add(rv)
        elif rv.nickname != nickname:
            rv.nickname = nickname
            db.session.commit()
        return rv


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40))
    is_early_access = db.Column(db.Boolean)
    last_checked = db.Column(db.Date)
    
    def __init__(self, title, is_early_access=False):
        self.title = title
        self.is_early_access = is_early_access


class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    
    def __init__(self, name):
        self.name = name


class Owned_Games(db.Model):
    __tablename__ = 'owned_games'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), primary_key=True)
    is_new = db.Column(db.Boolean)
    include = db.Column(db.Boolean)
    exclude = db.Column(db.Boolean)
    
    user = db.relationship(User, backref="owned_games")
    game = db.relationship(Game, backref="owned_games")

class Games_in_Store(db.Model):
    __tablename__ = 'games_in_store'
    #__table_args__ = (db.UniqueConstraint('store_id', 'game_id', name='_game_in_store'),)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), primary_key=True)
    game_store_id = db.Column(db.Integer)
    
    store = db.relationship(Store, backref="games_in_store")
    game = db.relationship(Game, backref="games_in_store")