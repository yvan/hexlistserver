'''
model for a link entry inside a hex
'''
from hexlistserver.app import db, flask_uuid

class LinkObject(db.Model):
    __tablename__ = 'link_objects'

    id = db.Column(db.String(), primary_key=True)
    url = db.Column(db.String())
    description = db.Column(db.String())
    hex_object_id = db.Column(db.Integer, db.ForeignKey('hex_objects.id', ondelete='CASCADE'))
    hex_object = db.relationship('HexObject', foreign_keys="LinkObject.hex_object_id")

    def __init__(self, url, description, hex_object_id):
        self.id = flask_uuid.uuid4()
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