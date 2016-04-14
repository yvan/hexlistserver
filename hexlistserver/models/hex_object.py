'''
model for a hex
'''
import random

from hexlistserver.app import db

class HexObject(db.Model):
    __tablename__ = 'hex_objects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    owner = db.Column(db.String())
    image_path = db.Column(db.String())
    hex_links = db.relationship('HexLink', backref="hex_object")

    def __init__(self, name, owner, image_path):
        self.id = random.randrange(2, 7890232)
        self.name = name
        self.owner = owner
        self.image_path = image_path

    def __repr__(self):
        return ('{{id: {}, ' 
            + 'name: "{}", ' 
            + 'owner: "{}", ' 
            + 'image_path: "{}"}}').format(
            self.id, 
            self.name, 
            self.owner, 
            self.image_path
            )

'''
author @yvan
http://flask-appbuilder.readthedocs.org/en/latest/relations.html
http://flask-sqlalchemy.pocoo.org/2.1/models/
http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#building-a-relationship
http://exploreflask.readthedocs.org/en/latest/storing.html
http://flask.pocoo.org/docs/0.10/quickstart/
http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#a-minimal-application
'''