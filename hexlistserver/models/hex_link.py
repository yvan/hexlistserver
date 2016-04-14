'''
model for a link entry inside a hex
'''
import random

from hexlistserver.app import db

class HexLink(db.Model):
    __tablename__ = 'hex_links'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    description = db.Column(db.String())
    hex_object_id = db.Column(db.Integer, db.ForeignKey('hex_objects.id'))

    def __init__(self, url, description, hex_object_id):
        self.id = random.randrange(2, 7890232)
        self.url = url
        self.description = description
        self.hex_object_id = hex_object_id

    def __repr__(self):
        return ('{{id: "{}",' 
            + 'url: "{}",' 
            + 'description: "{}",'
            + 'hex_object_id: "{}"}}').format(
            self.id, 
            self.url, 
            self.description,
            self.hex_object_id
            )

'''
author @yvan
'''