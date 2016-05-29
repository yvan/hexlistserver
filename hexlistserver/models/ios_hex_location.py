'''
model that show the location
of a hex on the ios platform
'''

from hexlistserver.app import db

class IosHexLocation(db.Model):
    __tablename__ = 'ios_hex_locations'

    hex_object_id = db.Column(db.String(), db.ForeignKey('hex_objects.id', ondelete='CASCADE'), primary_key=True)
    hex_object = db.relationship('HexObject', foreign_keys="IosHexLocation.hex_object_id")

    location = db.Column(db.String())

    def __init__(self, hex_object_id, location):
        self.hex_object_id = hex_object_id
        self.location = location

    def __repr__(self):
        return ('{{hex_object_id: "{}",'
            + 'location: "{}"}}').format(
            self.hex_object_id,
            self.location
            )
