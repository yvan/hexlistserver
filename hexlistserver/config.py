import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True
    SESSION_TYPE = os.environ['SESSION_TYPE']
    SECRET_KEY = os.environ['FLASK_SECRET_KEY']
    USER_MAKER_NAME = os.environ['USER_MAKER_NAME']
    USER_MAKER_PASSWORD = os.environ['USER_MAKER_PASSWORD']
    ANON_USER_ID = os.environ['ANON_USER_ID']
    ANON_USER_NAME = os.environ['ANON_USER_NAME']
    ANON_USER_PASSWORD = os.environ['ANON_USER_PASSWORD']
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    # MAILGUN_SENDER = os.environ['MAILGUN_SMTP_LOGIN']
    # MAILGUN_KEY = os.environ['MAILGUN_API_KEY']
    # MAILGUN_DOMAIN = os.environ['MAILGUN_DOMAIN']

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True

'''
    author @yvan
    configuration file for flask
    put sensitive info in instance/config.py
    read https://exploreflask.com/configuration.html
    read http://flask.pocoo.org/docs/0.10/config/
'''