from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID
import logging
from logging.handlers import RotatingFileHandler
from steamroller.lib import config


def config_logs(app):
    logging_level = config.get_option('LOGGING_LEVEL')
    formatter = logging.Formatter(
        "%(asctime)s;%(client_ip)s;%(filename)s:%(lineno)d;%(levelname)s;%(message)s")
    handler = RotatingFileHandler('/tmp/steamroller.log', maxBytes=10000, backupCount=1)
    logging.getLogger().setLevel(logging_level)
    handler.setLevel(logging_level)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)


app = Flask(__name__)
app.config.from_object('steamroller.lib.config.Flask_config')
db = SQLAlchemy(app)
oid = OpenID(app)
config_logs(app)

from steamroller.web import views, models
