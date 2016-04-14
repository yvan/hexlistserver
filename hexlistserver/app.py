'''
primary file with app logic
'''

import os

from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from hexlistserver.models import hex_object, hex_link, user

@app.route('/')
def heyo():
    return 'heyo!'

@app.route('/retrieve/<hexid>')
def retrieve_link(hexid):
    retrieved_hex = hex_object.query.filter_by(id=hexid).first()
    return 'you retrieved: {}'.format(hex)

@app.route('/store/<hexid>/<link>')
def store_link(hexid, link):
    hex_link_to_store = HexLink()
    hex_to_update = hex_object.query.filter_by(id=hexid).first()
    hex_to_update.hex_links.append(hex_link_to_store)
    db.session.commit()
    return 'you tried to store: {}'.format(link)

if __name__ == '__main__':
    app.run()

'''
http://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
'''