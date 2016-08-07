'''
model that show the location
of a hex on the ios platform
'''
import uuid

from hexlistserver.app import db

class IosHexLocation(db.Model):
    __tablename__ = 'ios_hex_locations'

    id = db.Column(db.String(), primary_key=True)
    user_object_id = db.Column(db.String(), db.ForeignKey('user_objects.id', ondelete="CASCADE"))
    hex_object_id = db.Column(db.String(), db.ForeignKey('hex_objects.id', ondelete="CASCADE"))    
    location = db.Column(db.String())

    hex_object = db.relationship('HexObject', foreign_keys="IosHexLocation.hex_object_id")
    user_object = db.relationship('UserObject', foreign_keys="IosHexLocation.user_object_id")

    def __init__(self, user_object_id, hex_object_id, location):
        self.id = uuid.uuid4().urn[9:] # make a uuid, convert to urn/string, uuid starts after 9th char
        self.user_object_id = user_object_id
        self.hex_object_id = hex_object_id
        self.location = location

    def __repr__(self):
        return ('{{hex_object_id: "{}",'
            + 'location: "{}"}}').format(
            self.hex_object_id,
            self.location
            )
