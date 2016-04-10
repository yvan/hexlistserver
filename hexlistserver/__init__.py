'''
    primary file with app logic
'''

import os

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

db = SQLAlchemy(app)

@app.route('/')
def heyo():
    return 'heyo!'
'''
    http://flask.pocoo.org/docs/0.10/quickstart/
'''
@app.route('/store/<link>')
def store_link(link):
    return 'you tried to store: {}'.format(link)
