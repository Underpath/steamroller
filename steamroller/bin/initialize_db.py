#!/usr/bin/env python2

from os import sys, path
sys.path.append('../..')
from steamroller.web import db
from steamroller.web import models

db.drop_all()

db.create_all()

steam = models.Store('Steam')
db.session.add(steam)

db.session.commit()
