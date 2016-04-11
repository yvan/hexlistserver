'''
model for a link entry inside a hex
'''
from hexlistserver import db
from sqlalchemy.dialects.postgresql import JSON

class HexLink(db.Model):
    __tablename__ = 'hex_links'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String())
    description = db.Column(db.String())
    hex_object = db.relationship("HexObject", back_populates="hex_links")

    def __init__(self, url, description):
        self.url = url
        self.description = description

    def __repr__(self):
        return ('<id {}>' 
            + '<url {}>' 
            + '<description {}>' 
            + '<image {}>' 
            + '<hex_links {}>').format(
            self.id, 
            self.url, 
            self.description
            )

'''
author @yvan
'''