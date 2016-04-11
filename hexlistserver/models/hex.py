'''
model for a hex
'''

from hexlistserver import db
from sqlalchemy.dialects.postgresql import JSON

class Hex(db.Model):
    __tablename__ = 'hexes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    owner = db.Column(db.Integer)
    image = db.Column(db.String())
    hex_links = db.Column(JSON)

    def __init__(self, name, owner, image, hex_links):
        self.name = name
        self.owner = owner
        self.image = image
        self.hex_links = hex_links

    def __repr__(self):
        return ('<id {}>' 
            + '<name {}>' 
            + '<owner {}>' 
            + '<image {}>' 
            + '<hex_links {}>').format(
            self.id, 
            self.name, 
            self.owner, 
            self.image, 
            ', '.join(self.hex_links)
            )

'''
author @yvan
http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#a-minimal-application
'''