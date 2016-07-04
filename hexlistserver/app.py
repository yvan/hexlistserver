'''
primary file with app logic
'''

import os
import re
import binascii
import requests
import traceback

from random_words import RandomWords
from flask import g, abort, redirect, url_for, request, Flask, render_template, jsonify, session, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from flask.ext.httpauth import HTTPBasicAuth

from hexlistserver.forms.textarea import TextareaForm
from hexlistserver.forms.create_user import CreateUser
from hexlistserver.forms.login_user import LoginUser

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

auth = HTTPBasicAuth()
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)

from hexlistserver.models import hex_object, link_object, user_object, ios_hex_location, send_object

'''
login manager
'''
@login_manager.user_loader
def load_user(user_id):
    user_obj = get_user_method(user_id)
    if user_obj:
        return user_obj
    return None

@app.route('/login_page', methods=['GET'])
def login_page():
    if not current_user.is_anonymous:
        return redirect(url_for('main_page'))
    login_user_form = LoginUser()
    return render_template('login.html', form=login_user_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous:
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        if verify_password(request.form['username'], request.form['password']):
            login_user(get_user_by_name(request.form['username']))
        else:
            # tell user about failed login
            flash('you failed to login')
    return redirect(url_for('login_page'))

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('main_page'))

'''
view route methods
'''

@app.route('/')
def main_page():
    text_area = TextareaForm()
    return render_template('main.html', form=text_area, show_login=current_user.is_anonymous)

@app.route('/about')
def about_page():
    # if a user is set in the context
    return render_template('about.html', show_login=current_user.is_anonymous)

# display a hex with all its links
@app.route('/hex/<string:hex_object_id>')
def hex_view(hex_object_id):

    hex_object = get_hex_object_method(hex_object_id)
    hex_owner = user_object.UserObject.query.filter_by(id=hex_object.user_object_id).first()
    hexlinks = link_object.LinkObject.query.filter_by(hex_object_id=hex_object_id)

    # if the hex is owned by anon, anonymous user
    # display a form to claim ownership
    if app.config['ANON_USER_NAME'] == hex_owner.username:
        
        # if the accessing user is logged in
        if not current_user.is_anonymous:
            create_user = CreateUser(username=current_user.username)
            text_area_form = TextareaForm()
            show_login = False
        # or if the hex is owned by someone else
        else:
            user_object_name = app.config['ANON_USER_NAME']
            create_user = CreateUser()
            text_area_form = None
            show_login = True

        return render_template('hex.html', form=create_user, textarea_form=text_area_form, hex_id=hex_object.id,  add_more_links=False, hex_name=hex_object.name, hexlinks=hexlinks, show_login=show_login)
    # if the hex is owned by someone else
    else:
        # if the accessing user is logged in is the owner
        if not current_user.is_anonymous and current_user.id == hex_owner.id:
            create_user = None
            text_area_form = TextareaForm()
            add_more_links = True
            show_login = False
        # or if the hex is owned by someone else
        # if the accessing user is not that owner
        elif  not current_user.is_anonymous:
            create_user = None
            text_area_form = None
            add_more_links = False
            show_login = False
        # if the user is not logged in
        else:
            create_user = None
            text_area_form = None
            add_more_links = False
            show_login = True

        return render_template('hex.html', form=create_user, textarea_form=text_area_form, hex_id=hex_object.id, add_more_links=add_more_links, hex_name=hex_object.name, hexlinks=hexlinks, show_login=show_login)

# display a link
@app.route('/link/<string:link_object_id>')
def link_view(link_object_id):
    link_object = get_link_method(link_object_id)
    return render_template('link.html', link=link_object, show_login=current_user.is_anonymous)

# display a user with all their hexes
@app.route('/user/<string:user_object_id>')
def user_view(user_object_id):
    hexlinks = {}
    user_object = get_user_method(user_object_id)
    hex_objects = hex_object.HexObject.query.filter_by(user_object_id=user_object.id)
    for hex_obj in hex_objects:
        links = link_object.LinkObject.query.filter_by(hex_object_id=hex_obj.id)
        hexlinks[hex_obj.id] = [link.url for link in links]
    return render_template('user.html', hexes=hex_objects, hexlinks=hexlinks, show_login=current_user.is_anonymous)

'''
internal form methods
'''
@app.route('/internal/form_hex_create', methods=['POST'])
def form_hex_create():
    text_area = TextareaForm(request.form)
    if request.form and text_area.validate_on_submit():
        # get a list of links from the input field
        submitted_urls = get_urls_from_blob(request.form['links'])
        # create a user?
        # create info for new hex, attributed to te "anon" user
        rw = RandomWords()
        name = 'hex-' + rw.random_word() + '-' + str(binascii.hexlify(os.urandom(16)))[2:-1]
        if not current_user.is_anonymous:
            user_id = current_user.id
            owner_id = current_user.id
        else:
            user_id = app.config['ANON_USER_ID']
            owner_id = app.config['ANON_USER_ID']
        image_path = ''

        #create new hex and new links
        new_hex_object = post_hex_object_method(name, owner_id, user_id, image_path)
        for url in submitted_urls:
            post_link_method(url, '', new_hex_object.id)
        return redirect(url_for('hex_view', hex_object_id=new_hex_object.id))
    text_area = TextareaForm(links=request.form['links'])
    return render_template('main.html', form=text_area, show_login=current_user.is_anonymous)

@app.route('/internal/form_make_or_claim_user_and_claim_hex/<string:hex_object_id>', methods=['POST'])
def form_create_user(hex_object_id):
    create_user = CreateUser(request.form)
    if request.form and create_user.validate_on_submit(): 
        if request.form['password'] == request.form['password_two'] and verify_password(request.form['username'], request.form['password']):
                # get user from their session
                if current_user.is_anonymous:
                    session_user_object = get_user_by_name(request.form['username'])
                    session['user_object_id'] = session_user_object.id
                else:
                    session_user_object = current_user
                # assign the hex to that user
                hex_to_reassign = get_hex_object_method(hex_object_id)
                hex_to_reassign.owner_id = session_user_object.id
                hex_to_reassign.user_object_id = session_user_object.id
                db.session.commit()
        elif request.form['password'] == request.form['password_two']:
            # create the user
            created_user = post_user_method(request.form['username'], request.form['password'], app.config['USER_MAKER_NAME'])
            # assign the hex to that user
            hex_to_reassign = get_hex_object_method(hex_object_id)
            hex_to_reassign.owner_id = created_user.id
            hex_to_reassign.user_object_id = created_user.id
            db.session.commit()
        else:
            abort(400)
        hexlinks = link_object.LinkObject.query.filter_by(hex_object_id=hex_object_id)
        return redirect(url_for('hex_view', hex_object_id=hex_object_id))

@app.route('/internal/form_add_links_to_hex/<string:hex_object_id>', methods=['POST'])
def form_add_links_to_hex(hex_object_id):
    text_area = TextareaForm(request.form)
    submitted_urls = get_urls_from_blob(request.form['links'])
    return redirect(url_for('hex_view', hex_object_id=hex_object_id))

'''
api route methods
'''

@app.route('/api/v1.0/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    # get the user inside curl -u user:password, and use them to generate a token
    # with that user's id
    token = get_auth_token_method()
    return jsonify({ 'token': token.decode('ascii') }), 200    

def get_auth_token_method():
    return g.user_object.generate_auth_token()

@app.route('/api/v1.0/hex/<string:hex_object_id>', methods=['GET'])
@auth.login_required
def get_hex_object(hex_object_id):
    retrieved_hex_object = get_hex_object_method(hex_object_id)
    if retrieved_hex_object:
        return jsonify({'id':retrieved_hex_object.id, 'name':retrieved_hex_object.name, 'image_path':retrieved_hex_object.image_path, 'owner_id':retrieved_hex_object.owner_id, 'user_id':retrieved_hex_object.user_object_id}), 200
    else:
        return jsonify({'error': 'we couldn\'t find that hex, u must be wrong', 'code': 404}), 404

def get_hex_object_method(hex_object_id):
    return hex_object.HexObject.query.filter_by(id=hex_object_id).first()

@app.route('/api/v1.0/hex', methods=['POST'])
@auth.login_required
def post_hex_object():
    name = request.json.get('name')
    user_id = request.json.get('user_id')
    owner_id = request.json.get('owner_id')
    image_path = request.json.get('image_path')

    #create new hex
    if name is None or user_id is None or owner_id is None or image_path is None:
        abort(400)

    new_hex_object = post_hex_object_method(name, owner_id, user_id, image_path)
    return jsonify({'id':new_hex_object.id, 'name':new_hex_object.name, 'image_path':new_hex_object.image_path, 'owner_id':new_hex_object.owner_id, 'user_id':new_hex_object.user_object_id}), 201

def post_hex_object_method(name, owner_id, user_id, image_path):
    new_hex_object = hex_object.HexObject(name, owner_id, user_id, image_path)
    db.session.add(new_hex_object)
    db.session.commit()
    return new_hex_object

@app.route('/api/v1.0/hex/<string:hex_object_id>', methods=['DELETE'])
@auth.login_required
def delete_hex(hex_object_id):
    delete_hex_method(hex_object_id)
    return  jsonify({'id':hex_object_delete.id, 'name':hex_object_delete.name, 'image_path':hex_object_delete.image_path, 'owner_id':hex_object_delete.owner_id, 'user_id':hex_object_delete.user_object_id}), 200

def delete_hex_method(hex_object_id):
    hex_object_delete = hex_object.HexObject.query.filter_by(id=hex_object_id).first()
    db.session.delete(hex_object_delete)
    db.session.commit()
    return hex_object_delete

@app.route('/api/v1.0/user/<string:user_object_id>', methods=['GET'])
@auth.login_required
def get_user(user_object_id):
    retrieved_user = get_user_method(user_object_id)
    if retrieved_user:
        return jsonify({'id':retrieved_user.id, 'username':retrieved_user.username}), 200
    else:
        return jsonify({'error': 'no user found for that id', 'code': 404}), 404

def get_user_method(user_object_id):
    return user_object.UserObject.query.filter_by(id=user_object_id).first()

def get_user_by_name(username):
    return user_object.UserObject.query.filter_by(username=username).first()

@app.route('/api/v1.0/user', methods=['POST'])
@auth.login_required
def post_user():
    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        abort(400)
    if user_object.UserObject.query.filter_by(username=username).first() is not None:
        abort(400)

    user = post_user_method(username, password, request.authorization.username)

    if user:
        return jsonify({'id': user.id, 'username': user.username}), 201
    else:
        return jsonify({'error': 'POST /user is forbidden api endpoint for the user you tried to authenticate with', 'code': 403}), 403

def post_user_method(username, password, req_auth_user):
    user = user_object.UserObject(username=username)
    user.hash_password(password)
    if req_auth_user == app.config['USER_MAKER_NAME']:
        db.session.add(user)
        db.session.commit()
        return user
    return None

@app.route('/api/v1.0/user/<string:user_object_id>', methods=['DELETE'])
@auth.login_required
def delete_user(user_object_id):
    user_delete = delete_user_method(user_object_id, request.authorization.username)
    if user_delete:
        return jsonify({'id': user_delete.id, 'username': user_delete.username}), 200
    else:
        return jsonify({'error': 'DELETE /user is forbidden api endpoint for the user you provided', 'code': 403}), 403

def delete_user_method(user_object_id, req_auth_user):
    user_delete = user_object.UserObject.query.filter_by(id=user_object_id).first()
    if req_auth_user == app.config['USER_MAKER_NAME']:
        db.session.delete(user_delete)
        db.session.commit()
        return user_delete
    return None   

@app.route('/api/v1.0/link/<string:link_object_id>', methods=['GET'])
@auth.login_required
def get_link(link_object_id):
    retrieved_link = get_link_method(link_object_id)
    if retrieved_link:
        return jsonify({'id': retrieved_link.id, 'url': retrieved_link.url,'description': retrieved_link.description,'hex_object_id': retrieved_link.hex_object_id}), 200
    else:
        return jsonify({'error': 'we couldn\'t find that link, u must be wrong', 'code': 404}), 404

@app.route('/api/v1.0/hexlinks/<string:hex_object_id>', methods=['GET'])
@auth.login_required
def get_hexlinks(hex_object_id):
    return_links = link_object.LinkObject.query.filter_by(hex_object_id=hex_object_id)
    if return_links:
        return jsonify({'hexlinks': [{'id': retrieved_link.id, 'url': retrieved_link.url,'description': retrieved_link.description,'hex_object_id': retrieved_link.hex_object_id} for retrieved_link in return_links]}), 200
    else:
        return jsonify({'error': 'we couldn\'t find those links, u must be wrong', 'code': 404}), 404

def get_link_method(link_object_id):
    return link_object.LinkObject.query.filter_by(id=link_object_id).first()

#accepts multiple urls, so a list
@app.route('/api/v1.0/link', methods=['POST'])
@auth.login_required
def post_link():
    url =  request.json.get('url')
    description =  request.json.get('description')
    hex_object_id =  request.json.get('hex_object_id')
    if url is None or hex_object_id is None:
        abort(400)
    new_link_object = post_link_method(url, description, hex_object_id)
    return jsonify({'id': new_link_object.id, 'urls': new_link_object.url,'description': new_link_object.description,'hex_object_id': new_link_object.hex_object_id}), 201

#accepts multiple urls, so a list
@app.route('/api/v1.0/hexlinks', methods=['POST'])
@auth.login_required
def post_hexlinks():
    return_links = []
    for link in request.json:
        url = link.get('url')
        description = link.get('description')
        hex_object_id = link.get('hex_object_id')
        print('aborting on link {}'.format(link))
        if url is None or hex_object_id is None:
            abort(400)
        new_link_object = post_link_method(url, description, hex_object_id)
        return_links.append(new_link_object)
    return jsonify({i:{'id': new_link_object.id, 'urls': new_link_object.url,'description': new_link_object.description,'hex_object_id': new_link_object.hex_object_id} for i, new_link_object in enumerate(return_links)}), 201

def post_link_method(url, description, hex_object_id):
    new_link_object = link_object.LinkObject(url, description, hex_object_id)
    db.session.add(new_link_object)
    db.session.commit()
    return new_link_object

@app.route('/api/v1.0/link/<string:link_object_id>', methods=['DELETE'])
@auth.login_required
def delete_link(link_object_id):
    delete_link = delete_link_method(link_object_id)
    return jsonify({'id': delete_link.id, 'url': delete_link.url,'description': delete_link.description,'hex_object_id': delete_link.hex_object_id}), 200

@app.route('/api/v1.0/hexlinks/<string:hex_object_id>', methods=['DELETE'])
@auth.login_required
def delete_hexlinks(hex_object_id):
    delete_links = []
    return_links = link_object.LinkObject.query.filter_by(hex_object_id=hex_object_id)
    for link in return_links:
        delete_links.append(delete_link_method(link.id))
    return jsonify({'hexlinks': [{'id': delete_link.id, 'url': delete_link.url,'description': delete_link.description,'hex_object_id': delete_link.hex_object_id} for delete_link in delete_links]}), 200

def delete_link_method(link_object_id):
    delete_link = link_object.LinkObject.query.filter_by(id=link_object_id).first()
    db.session.delete(delete_link)
    db.session.commit()
    return delete_link

@app.route('/api/v1.0/location', methods=['GET'])
@auth.login_required
def get_location():
    hex_object_id = request.json.get('hex_object_id')
    user_object_id = request.json.get('user_object_id')
    return_location = get_location_method(user_object_id, hex_object_id)
    if return_location:
        return jsonify({'id': return_location.id,'user_object_id': return_location.user_object_id,'hex_object_id': return_location.hex_object_id, 'location': return_location.location}), 200
    else:
        return jsonify({'error': 'we couldn\'t find that location, u must be wrong', 'code': 404}), 404

def get_location_method(user_object_id, hex_object_id):
    return ios_hex_location.IosHexLocation.query.filter_by(user_object_id=user_object_id, hex_object_id=hex_object_id).first()

@app.route('/api/v1.0/location', methods=['POST'])
@auth.login_required
def post_location():
    platform = request.json.get('platform')
    location = request.json.get('location')
    hex_object_id = request.json.get('hex_object_id')
    user_object_id = request.json.get('hex_object_id')
    if location is None or hex_object_id is None or platform is None:
        abort(400)
    if platform == 'ios':
        new_hex_location = post_location_method(user_object_id, hex_object_id, location)
    else:
        abort(400)
    return jsonify({'id': new_hex_location.id,'user_object_id': new_hex_location.user_object_id,'hex_object_id': new_hex_location.hex_object_id, 'location': new_hex_location.location}), 201

def post_location_method(user_object_id, hex_object_id, location):
    new_hex_location = ios_hex_location.IosHexLocation(user_object_id, hex_object_id, location)
    db.session.add(new_hex_location)
    db.session.commit()
    return new_hex_location

@app.route('/api/v1.0/location/<string:location_object_id>', methods=['DELETE'])
@auth.login_required
def delete_location(location_object_id):
    hex_location = delete_location_method(location_object_id)
    return jsonify({'id': hex_location.id,'user_object_id': hex_location.user_object_id,'hex_object_id': hex_location.hex_object_id, 'location': hex_location.location}), 200

def delete_location_method(location_object_id):
    hex_location = ios_hex_location.IosHexLocation.query.filter_by(id=location_object_id).first()
    db.session.delete(hex_location)
    db.session.commit()
    return hex_location

@app.route('/api/v1.0/send/<string:hex_object_id>', methods=['GET'])
@auth.login_required
def get_send(hex_object_id):
    retrieved_send_object = get_send_method(hex_object_id)
    if retrieved_send_object:
        return jsonify({'id': retrieved_send_object.id, 'sender_id': retrieved_send_object.sender_id, 'recipient_id': retrieved_send_object.recipient_id, 'hex_object_id':retrieved_send_object.hex_object_id}), 200
    else:
        return jsonify({'error': 'we couldn\'t find that send, u must be wrong', 'code': 404}), 404

def get_send_method(hex_object_id):
    return send_object.SendObject.query.filter_by(id=hex_object_id).first()

@app.route('/api/v1.0/send', methods=['POST'])
@auth.login_required
def post_send():
    sender_id = request.json.get('sender_id')
    recipient_id = request.json.get('recipient_id')
    hex_object_id = request.json.get('hex_object_id')
    if sender_id is None or recipient_id is None or hex_object_id is None:
        abort(400)
    new_send_object = post_send_method(sender_id, recipient_id, hex_object_id)
    return jsonify({'sender_id': new_send_object.sender_id, 'recipient_id': new_send_object.recipient_id, 'hex_object_id':new_send_object.hex_object_id}), 201

def post_send_method(sender_id, recipient_id, hex_object_id):
    new_send_object = send_object.SendObject(sender_id, recipient_id, hex_object_id)
    db.session.add(new_send_object)
    db.session.commit()
    return new_send_object    

@app.route('/api/v1.0/send/<string:hex_object_id>', methods=['DELETE'])
@auth.login_required
def delete_send(hex_object_id):
    send_object_delete = delete_send_method(hex_object_id)
    return jsonify({'sender_id': send_object_delete.sender_id, 'recipient_id': send_object_delete.recipient_id, 'hex_object_id':send_object_delete.hex_object_id}), 200

def delete_send_method(hex_object_id):
    send_object_delete = send_object.SendObject.query.filter_by(hex_object_id=hex_object_id).first()
    db.session.delete(send_object_delete)
    db.session.commit()
    return send_object_delete

'''
supporting non route methods
'''

# get the urls from a blob of text
def get_urls_from_blob(blob):
    WEB_URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    submitted_urls = re.findall(WEB_URL_REGEX, blob)
    return submitted_urls

# this error handler only fires when DEBUG=False,
# so it only fires on our production server
@app.errorhandler(500)
def internal_error(error):
    r = send_mail('yvanscher@gmail.com', app.config['MAILGUN_SENDER'], '500 server error', '\n'.join(traceback.format_stack()), None)
    return jsonify({'error': 'there was some terrible error, an email is on its way to us, don\'t fret little human', 'code': 500}), 500

def send_mail(to_address, from_address, subject, plaintext, html):
    r = requests.post("https://api.mailgun.net/v2/%s/messages" % app.config['MAILGUN_DOMAIN'],
            auth=("api", app.config['MAILGUN_KEY']),
            data={
                "from": from_address,
                "to": to_address,
                "subject": subject,
                "text": plaintext,
                "html": html
            }
         )
    return r

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