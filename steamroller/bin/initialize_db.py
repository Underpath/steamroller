#!/usr/bin/env python3

from steamroller import db, models

db.drop_all()

db.create_all()

steam = models.Store('Steam')
db.session.add(steam)

db.session.commit()
