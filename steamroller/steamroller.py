from flask import Flask
from flask_openid import OpenID
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

from . import config


def setup_logs(app):
    handler = config.get_log_handler()
    app.logger.addHandler(handler)


app = Flask(__name__)
setup_logs(app)
app.config.from_object("steamroller.config.Flask_config")
db = SQLAlchemy(app)
oid = OpenID(app)
sess = Session()
sess.init_app(app)
csrf = CSRFProtect(app)

from . import models, views
