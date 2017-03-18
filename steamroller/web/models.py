from steamroller.web import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    steam_id = db.Column(db.String(40))
    nickname = db.Column(db.String(80))

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
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False