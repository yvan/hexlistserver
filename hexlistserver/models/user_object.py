'''
model for a user
'''

import random

from hexlistserver.app import db

class UserObject(db.Model):
    __tablename__ = 'user_objects'

    id = db.Column(db.Integer, primary_key=True)

    def __init__(self):
        self.id = random.randrange(2, 7890232)

    def __repr__(self):
        return ('{{id: "{}"}}').format(
            self.id
            )

'''
author @yvan
'''