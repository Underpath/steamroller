from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_openid import OpenID

app = Flask(__name__)
app.config.from_object('steamroller.lib.config.Flask_config')
db = SQLAlchemy(app)
oid = OpenID(app)

from steamroller.web import views, models
