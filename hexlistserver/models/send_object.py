'''
an object representing sends from one user to another
'''
import uuid

from hexlistserver.app import db

class SendObject(db.Model):
    __tablename__ = 'send_objects'

    id = db.Column(db.String(), primary_key=True)
    sender_id = db.Column(db.String(), index=True)
    recipient_id = db.Column(db.String(), index=True)
    hex_object_id = db.Column(db.String(), db.ForeignKey('hex_objects.id', ondelete="CASCADE"))
    hex_object = db.relationship('HexObject', foreign_keys="SendObject.hex_object_id")

    def __init__(self, sender_id, recipient_id, hex_object_id):
        self.id = uuid.uuid4().urn[9:]
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.hex_object_id = hex_object_id

    def __repr__(self):
        return ('{{sender_id: "{}",'
            + 'recipient_id: "{}",'
            + 'hex_object_id: "{}"}}').format(
            self.sender_id,
            self.recipient_id,
            self.hex_object_id
            )