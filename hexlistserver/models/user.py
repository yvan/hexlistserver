'''
model for a user
'''

import random

from hexlistserver.app import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    owned_hex_objects = db.relationship('HexObject', backref='owner')
    user_hex_objects = db.relationship('HexObject', backref='user')

    def __init__(self, url, description, hex_object_id):
        self.id = random.randrange(2, 7890232)
        self.url = url

    def __repr__(self):
        return ('{{id: "{}",' 
            + 'url: "{}"}}').format(
            self.id, 
            self.url
            )

'''
author @yvan
'''