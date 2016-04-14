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

from hexlistserver.models import hex_object, hex_link, user

@app.route('/')
def heyo():
    return 'heyo it\'s hexlist!'

@app.route('/hex/get/<int:hex_object_id>', methods=['GET'])
def get_hex_object(hex_object_id):
    retrieved_hex = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    return 'you retrieved: {}'.format(retrieved_hex)

@app.route('/hex/post/', methods=['GET', 'POST'])
def post_hex_object():
    new_hex_object = hex_object.HexObject(request.args.get('name'), request.args.get('owner'), request.args.get('image_path'))
    db.session.add(new_hex_object)
    db.session.commit()
    return 'you stored: {}'.format(new_hex_object)

@app.route('/hex/delete/<int:hex_object_id>')
def delete_hex(hex_object_id):
    hex_object_delete = hex_object.HexObject.query.filter_by(id=hex_object_id)
    db.session.delete(hex_object_delete)
    db.session.commit()
    return 'you deleted hex with id: {}'.format(hex_object_id)

@app.route('/user/post?', methods=['POST'])
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