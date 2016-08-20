'''
an object representing sends from one user to another
'''
import uuid

from hexlistserver.app import db

class PasswordReset(db.Model):
    __tablename__ = 'password_resets'

    id = db.Column(db.String(), primary_key=True)
    code = db.Column(db.String())
    expiry_date = db.Column(db.String())
    user_object_id = db.Column(db.String(), db.ForeignKey('user_objects.id', ondelete="CASCADE"))
    user_object = db.relationship('UserObject', foreign_keys="PasswordReset.user_object_id")

    def __init__(self, code, user_object_id, expiry_date):
        self.id = uuid.uuid4().urn[9:]
        self.code = code
        self.user_object_id = user_object_id
        self.expiry_date = expiry_date

    def __repr__(self):
        return ('{{id: "{}"'
            + 'code: "{}",'
            + 'user_object_id: "{}",'
            + 'expiry_date: "{}"}}').format(
            self.id,
            self.code,
            self.user_object_id,
            self.expiry_date
        )