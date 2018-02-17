#!/usr/bin/env python2

from os import sys
sys.path.append('..')
from steamroller import db
import models

db.drop_all()

db.create_all()

steam = models.Store('Steam')
db.session.add(steam)

db.session.commit()
