'''
model for a hex
'''
from hexlistserver.app import db, flask_uuid

class HexObject(db.Model):
    __tablename__ = 'hex_objects'

    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String())
    image_path = db.Column(db.String())

    owner_id = db.Column(db.Integer, db.ForeignKey('user_objects.id', ondelete='CASCADE'))
    user_object_id = db.Column(db.Integer, db.ForeignKey('user_objects.id', ondelete='CASCADE'))

    owner = db.relationship('UserObject', foreign_keys="HexObject.owner_id")
    user_object = db.relationship('UserObject', foreign_keys="HexObject.user_object_id")

    def __init__(self, name, owner_id, user_id, image_path):
        self.id = self.id = flask_uuid.uuid4()
        self.name = name
        self.owner_id = owner_id
        self.user_object_id = user_id
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
            self.user_id,
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