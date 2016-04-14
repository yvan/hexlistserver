'''
model for a link entry inside a hex
'''
from app import db

class HexLink(db.Model):
    __tablename__ = 'hex_links'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    description = db.Column(db.String())
    hex_object_id = db.Column(db.Integer, db.ForeignKey('hex_objects.id'))

    def __init__(self, url, description):
        self.url = url
        self.description = description

    def __repr__(self):
        return ('<id {}>' 
            + '<url {}>' 
            + '<description {}>').format(
            self.id, 
            self.url, 
            self.description
            )

'''
author @yvan
'''