import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

class ProductionConfig(Config):
    DEVELOPMENT = False
    DEBUG = False
    MAIL_SERVER=os.environ['MAIL_SERVER']
    MAIL_PORT=os.environ['MAIL_PORT']
    MAIL_USE_TLS=False
    MAIL_USE_SSL=True
    MAIL_USERNAME=os.environ['MAIL_USERNAME']
    MAIL_PASSWORD=os.environ['MAIL_PASSWORD']

    # MAIL_SERVER=os.environ['MAILGUN_SMTP_SERVER']
    # MAIL_PORT=os.environ['MAILGUN_SMTP_PORT']
    # MAIL_USE_TLS=False
    # MAIL_USE_SSL=True
    # MAIL_USERNAME=os.environ['MAILGUN_SMTP_LOGIN']
    # MAIL_PASSWORD=os.environ['MAILGUN_SMTP_PASSWORD']

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