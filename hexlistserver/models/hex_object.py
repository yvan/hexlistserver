'''
model for a hex
'''

from hexlistserver import db
from sqlalchemy.dialects.postgresql import JSON
from hexlistserver.models import hex_link, link, user

class HexObject(db.Model):
    __tablename__ = 'hex_objects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    owner = db.Column(db.String())
    image_path = db.Column(db.String())
    hex_links = db.relationship("HexLink", back_populates="hex_object")

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
http://flask-sqlalchemy.pocoo.org/2.1/models/
http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#building-a-relationship
http://exploreflask.readthedocs.org/en/latest/storing.html
http://flask.pocoo.org/docs/0.10/quickstart/
http://flask-sqlalchemy.pocoo.org/2.1/quickstart/#a-minimal-application
'''