'''
model for a user
'''

from hexlistserver.app import app, db, flask_uuid

from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

class UserObject(db.Model):
    __tablename__ = 'user_objects'

    id = db.Column(db.String(), primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username):
        self.id = flask_uuid.uuid4()
        self.username = username

    def __repr__(self):
        return ('{{id: "{}"}}').format(
            self.id,
            self.username
            )

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=86400):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = UserObject.query.get(data['id'])
        return user

'''
author @yvan
'''