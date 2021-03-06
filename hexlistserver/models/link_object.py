'''
model for a link entry inside a hex
'''
import uuid

from hexlistserver.app import db

class LinkObject(db.Model):
    __tablename__ = 'link_objects'

    id = db.Column(db.String(), primary_key=True)
    url = db.Column(db.String(), index=True)
    description = db.Column(db.String(), index=True)
    web_page_title = db.Column(db.String(), index=True)
    hex_object_id = db.Column(db.String(), db.ForeignKey('hex_objects.id', ondelete="CASCADE"))
    hex_object = db.relationship('HexObject', foreign_keys="LinkObject.hex_object_id")

    def __init__(self, url, description, hex_object_id):
        self.id = uuid.uuid4().urn[9:] # make a uuid, convert to urn/string, uuid starts after 9th char
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