'''
primary file with app logic
'''

import os

from flask import g, abort, redirect, url_for, request, Flask, render_template, jsonify

from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.login import LoginManager, login_required
from flask.ext.uuid import FlaskUUID

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
login_manager = LoginManager()
auth = HTTPBasicAuth()
login_manager.init_app(app)
db = SQLAlchemy(app)
flask_uuid = FlaskUUID(app)

from hexlistserver.models import hex_object, link_object, user_object

@app.route('/')
def heyo():
    return 'heyo it\'s hexlist!'

@app.route('/api/v1.0/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    # get the user inside curl -u user:password, and use them to generate a token
    # with that user's id
    token = g.user_object.generate_auth_token()
    return jsonify({ 'token': token.decode('ascii') }), 200

@app.route('/api/v1.0/hex/<int:hex_object_id>', methods=['GET'])
@auth.login_required
def get_hex_object(hex_object_id):
    retrieved_hex_object = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    return jsonify({ 'hex': str(retrieved_hex_object) }), 200

@app.route('/api/v1.0/hex', methods=['POST'])
@auth.login_required
def post_hex_object():
    name = request.json.get('name')
    user_id = request.json.get('user_id')
    owner_id = request.json.get('owner_id')
    image_path = request.json.get('image_path')
    if name is None or user_id is None or owner_id is None or image_path is None:
        abort(400)
    new_hex_object = hex_object.HexObject(name, owner_id, user_id, image_path)
    db.session.add(new_hex_object)
    db.session.commit()
    return jsonify({ 'hex': str(new_hex_object) }), 201

@app.route('/api/v1.0/hex/<int:hex_object_id>', methods=['DELETE'])
@auth.login_required
def delete_hex(hex_object_id):
    hex_object_delete = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    db.session.delete(hex_object_delete)
    db.session.commit()
    return  jsonify({ 'hex_id': hex_object_id }), 200

@app.route('/api/v1.0/user/<int:user_object_id>', methods=['GET'])
@auth.login_required
def get_user(user_object_id):
    retrieved_user = user_object.UserObject.query.filter_by(id=user_object_id).first()
    return jsonify({ 'username': retrieved_user.username }), 200

@app.route('/api/v1.0/user', methods=['POST'])
@auth.login_required
def post_user():
    username = request.json.get('username')
    password = request.json.get('password')
    user = user_object.UserObject(username=username)
    user.hash_password(password)
    if username is None or password is None:
        abort(400)
    if user_object.UserObject.query.filter_by(username=username).first() is not None:
        abort(400)
    db.session.add(user)
    db.session.commit()
    return jsonify({ 'username': user.username }), 201, {'location': url_for('get_user', user_object_id=user.id, _external = True)}

@app.route('/api/v1.0/user/<int:user_object_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_object_id):
    user_delete = user_object.UserObject.query.filter_by(id=user_object_id).first()
    db.session.delete(user_delete)
    db.session.commit()
    return jsonify({ 'user_object_id': user_delete.id}), 200

@app.route('/api/v1.0/link/<int:link_object_id>', methods=['GET'])
@auth.login_required
def get_link(link_object_id):
    retrieved_link = link_object.LinkObject.query.filter_by(id=link_object_id).first()
    return jsonify({ 'link_object_id': retrieved_link.id})

@app.route('/api/v1.0/link', methods=['POST'])
@auth.login_required
def post_link():
    url = request.json.get('url')
    description = request.json.get('description')
    hex_object_id = request.json.get('hex_object_id')
    if url is None or description is None or hex_object_id is None:
        abort(400)
    new_link_object = link_object.LinkObject(url, description, hex_object_id)
    db.session.add(new_link_object)
    db.session.commit()
    return jsonify({ 'link_object': str(new_link_object) }), 201

@app.route('/api/v1.0/link/<int:link_object_id>', methods=['DELETE'])
@auth.login_required
def delete_link(link_object_id):
    delete_link = link_object.LinkObject.query.filter_by(id=link_object_id).first()
    db.session.delete(delete_link)
    db.session.commit()
    return jsonify({ 'link_object_id': delete_link.id}), 200  

@auth.verify_password
def verify_password(username_or_token, password):
    user = user_object.UserObject.verify_auth_token(username_or_token)
    if not user:
        user = user_object.UserObject.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user_object = user
    return True

if __name__ == '__main__':
    app.run()

'''
author @yvan
http://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information
'''