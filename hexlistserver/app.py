'''
primary file with app logic
'''

import os

from flask import request
from flask import Flask, render_template
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from hexlistserver.models import hex_object, hex_link, user_object

@app.route('/')
def heyo():
    return 'heyo it\'s hexlist!'

@app.route('/hex/<int:hex_object_id>', methods=['GET'])
def get_hex_object(hex_object_id):
    retrieved_hex_object = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    return 'you retrieved: {}'.format(retrieved_hex_object)

@app.route('/hex/', methods=['POST'])
def post_hex_object():
    new_hex_object = hex_object.HexObject(request.args.get('name'), request.args.get('owner_id'), request.args.get('image_path'))
    db.session.add(new_hex_object)
    db.session.commit()
    return 'you stored: {}'.format(new_hex_object)

@app.route('/hex/<int:hex_object_id>', methods=['DELETE'])
def delete_hex(hex_object_id):
    hex_object_delete = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    db.session.delete(hex_object_delete)
    db.session.commit()
    return 'you deleted hex with id: {}'.format(hex_object_id)

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    retrieved_user_object = user_object.UserObject.query.filter_by(id=user_id).first()
    return 'you queried: {}'.format(retrieved_user_object)

@app.route('/user/', methods=['POST'])
def post_user():
    new_user_object = user_object.UserObject()
    db.session.add(new_user_object)
    db.session.commit()
    return 'you made user with id: {}'.format(new_user_object.id)

@app.route('/user/<int:user_object_id>', methods=['DELETE'])
def delete_user(user_object_id):
    user_object_delete = user_object.UserObject.query.filter_by(id=user_object_id).first()
    db.session.delete(user_object_delete)
    db.session.commit()
    return 'you deleted user with id: {}'.format(user_object_id)

if __name__ == '__main__':
    app.run()

'''
author @yvan
http://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
'''