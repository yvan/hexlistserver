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
    return 'heyo it\'s hexlist!'

@app.route('/hex/get/<int:hex_object_id>', methods=['GET'])
def get_hex_object(hex_object_id):
    retrieved_hex = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    return 'you retrieved: {}'.format(retrieved_hex)

@app.route('/hex/post/<int:hex_object_id>', methods=['POST'])
def post_hex_object(hexid, link):
    hex_link_to_store = hex_link.HexLink()
    hex_to_create = hex_object.HexObject.query.filter_by(id=hexid).first()
    hex_to_create.hex_links.append(hex_link_to_store)
    db.session.commit()
    return 'you tried to store: {}'.format(link)

@app.route('/hex/delete/<int:hex_object_id>')
def delete_hex(hex_object_id):
    hex_object.HexObject.query.filter_by(id=hex_object_id).delete()
    return 'you deleted hex with id: {}'.format(hex_object_id)

@app.route('/user/post?q', methods=['POST'])
def post_user():
    pass

@app.route('/user/get/<int:user_id>', methods=['GET'])
def get_user():
    pass

if __name__ == '__main__':
    app.run()

'''
author @yvan
http://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
'''