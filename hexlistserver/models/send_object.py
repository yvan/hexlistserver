from hexlistserver.app import db

class SendObject(db.Model):
    __tablename__ = 'send_objects'

    sender_id = db.Column(db.String())
    recipient_id = db.Column(db.String())
    hex_object_id = db.Column(db.String(), db.ForeignKey('hex_objects.id', ondelete='CASCADE'), primary_key=True)
    hex_object = db.relationship('HexObject', foreign_keys="SendObject.hex_object_id")

    def __init__(self, sender_id, recipient_id, hex_object_id):
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