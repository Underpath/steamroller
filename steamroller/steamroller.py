from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID
from flask_wtf.csrf import CSRFProtect
import config


def setup_logs(app):
    handler = config.get_log_handler()
    app.logger.addHandler(handler)


app = Flask(__name__)
app.config.from_object('steamroller.config.Flask_config')
db = SQLAlchemy(app)
oid = OpenID(app)
csrf = CSRFProtect(app)
setup_logs(app)

import views, models
