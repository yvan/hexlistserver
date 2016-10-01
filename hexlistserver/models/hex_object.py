'''
model for a hex
'''

import uuid

from hexlistserver.app import db

class HexObject(db.Model):
    __tablename__ = 'hex_objects'

    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String(), index=True)
    image_path = db.Column(db.String(), index=True)

    is_private = db.Column(db.Boolean)

    owner_id = db.Column(db.String(), db.ForeignKey('user_objects.id'), index=True)
    user_object_id = db.Column(db.String(), db.ForeignKey('user_objects.id'), index=True)

    owner = db.relationship('UserObject', foreign_keys="HexObject.owner_id")
    user_object = db.relationship('UserObject', foreign_keys="HexObject.user_object_id")

    def __init__(self, name, owner_id, user_id, image_path, is_private):
        self.id = uuid.uuid4().urn[9:] # make a uuid, convert to urn/string, uuid starts after 9th char
        self.name = name
        self.owner_id = owner_id
        self.user_object_id = user_id
        self.is_private = is_private
        self.image_path = image_path

    def __repr__(self):
        return ('{{id: {}, ' 
            + 'name: "{}", ' 
            + 'owner_id: "{}", ' 
            + 'user_id: "{}", '
            + 'image_path: "{}"}}').format(
            self.id, 
            self.name, 
            self.owner_id,
            self.user_object_id,
            self.image_path
            )

'''
author @yvan
http://docs.sqlalchemy.org/en/latest/orm/join_conditions.html
http://docs.sqlalchemy.org/en/latest/orm/backref.html
http://flask-appbuilder.readthedocs.org/en/latest/relations.html
http://flask-sqlalchemy.pocoo.org/2.1/models/
http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#building-a-relationship
http://exploreflask.readthedocs.org/en/latest/storing.html
http://flask.pocoo.org/docs/0.10/quickstart/
http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#a-minimal-application
'''