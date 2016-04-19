'''
primary file with app logic
'''

import os

from flask import g, abort, redirect, url_for, request, Flask, render_template, jsonify

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.login import LoginManager, login_required

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
auth = HTTPBasicAuth()
login_manager.init_app(app)
db = SQLAlchemy(app)

from hexlistserver.models import hex_object, hex_link, user_object

@app.route('/')
def heyo():
    return 'heyo it\'s hexlist!'

@app.route('/api/token')
def get_auth_token():
    token = g.user_object.User.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') })

@app.route('/api/v1.0/hex/<int:hex_object_id>', methods=['GET'])
@auth.login_required
def get_hex_object(hex_object_id):
    retrieved_hex_object = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    return 'you retrieved: {}'.format(retrieved_hex_object)

@app.route('/api/v1.0/hex/', methods=['POST'])
@auth.login_required
def post_hex_object():
    new_hex_object = hex_object.HexObject(request.args.get('name'), request.args.get('owner_id'), request.args.get('image_path'))
    db.session.add(new_hex_object)
    db.session.commit()
    return 'you stored: {}'.format(new_hex_object)

@app.route('/api/v1.0/hex/<int:hex_object_id>', methods=['DELETE'])
@auth.login_required
def delete_hex(hex_object_id):
    hex_object_delete = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    db.session.delete(hex_object_delete)
    db.session.commit()
    return 'you deleted hex with id: {}'.format(hex_object_id)

@app.route('/api/v1.0/user', methods=['GET'])
@auth.login_required
def get_user():
    user_object_id = request.json.get('user_object_id')
    retrieved_user_object = user_object.UserObject.query.filter_by(id=user_object_id).first()
    return jsonify({ 'username': retrieved_user_object.username }), 201

@app.route('/api/v1.0/user', methods=['POST'])
@auth.login_required
def post_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)
    if user_object.UserObject.query.filter_by(username=username).first() is not None:
        abort(400)
    user = user_object.UserObject(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', user_object_id=user.id, _external = True)}

@app.route('/api/v1.0/user/<int:user_object_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_object_id):
    user_object_delete = user_object.UserObject.query.filter_by(id=user_object_id).first()
    db.session.delete(user_object_delete)
    db.session.commit()
    return 'you deleted user with id: {}'.format(user_object_id)

@auth.verify_password
def verify_password(username, password):
    user = user_object.UserObject.query.filter_by(username = username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

if __name__ == '__main__':
    app.run()

'''
author @yvan
http://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
'''