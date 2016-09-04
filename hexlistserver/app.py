'''
primary file with app logic
'''

import os
import re
import bs4
import uuid
import petname
import binascii
import requests
import traceback

from rq import Queue
from datetime import datetime, timedelta
from urllib.parse import urlparse
from hexlistserver.worker import conn
from random_words import RandomWords
from itsdangerous import URLSafeSerializer, SignatureExpired, BadSignature
from postmark import PMMail

from flask import g, abort, redirect, url_for, request, Flask, render_template, jsonify, session, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from flask.ext.httpauth import HTTPBasicAuth
from flask.ext.sslify import SSLify
from flask_mail import Mail, Message

from hexlistserver.forms.textarea import TextareaForm
from hexlistserver.forms.create_user import CreateUser
from hexlistserver.forms.login_user import LoginUser
from hexlistserver.forms.input_email import InputEmail
from hexlistserver.forms.rename_hex import RenameHex
from hexlistserver.forms.rename_link import RenameLink
from hexlistserver.forms.recover_password import RecoverPassword
from hexlistserver.forms.reset_password import ResetPassword

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

auth = HTTPBasicAuth()
sslify = SSLify(app, subdomains=True)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
db = SQLAlchemy(app)
q = Queue(connection=conn)
mail = Mail(app)

from hexlistserver.models import hex_object, link_object, user_object, ios_hex_location, send_object, password_reset

'''
login manager
'''
@login_manager.user_loader
def load_user(user_id):
    user_obj = get_user_method(user_id)
    if user_obj:
        return user_obj
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_anonymous:
        return redirect(url_for('main_page'))
    if request.method == 'POST':
        if verify_password(request.form['username'], request.form['password']):
            login_user(get_user_by_name(request.form['username']))
            return redirect(url_for('user_view', username=current_user.username))
        else:
            # tell user about failed login
            flash('you failed to login')
            return redirect(url_for('login'))
    else:
        if not current_user.is_anonymous:
            return redirect(url_for('main_page'))
        login_user_form = LoginUser()
        return render_template('login.html', form=login_user_form)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(request.referrer)

@app.route('/signup', methods=['GET'])
def signup():
    create_user = CreateUser()
    return render_template('signup.html', form=create_user)

@app.route('/recover_password', methods=['GET', 'POST'])
def reset_password():
    # take in email, sign/encrpyt it,
    # then send a n email to that email 
    if request.method == 'POST':
        # we want our pwd resets to only last 30 min
        s = URLSafeSerializer(app.config['SECRET_KEY'])
        input_code = {"code": uuid.uuid4().urn[9:]}
        hashed_code_payload = s.dumps(input_code)
        user_to_email = get_user_by_email(request.form['email'])
        if not user_to_email:
            flash('the email you gave is not registered. this is awkward.')
        else:
            message = PMMail(api_key = app.config['POSTMARK_API_KEY'],
                     subject = "hexlist password reset",
                     sender = "wizard@hexlist.com",
                     to = request.form['email'],
                     text_body = '''
                                here is the link to reset your password:

                                http://hexlist.com/password_reset/{}

                                if you did not reset your password ignore this email or contact support: support@hexlist.com

                                '''.format(hashed_code_payload),
                     tag = "recover_password")
            j = q.enqueue(queue_mail, message)
            flash('we sent you an email. go look at it.')
            pass_reset = password_reset.PasswordReset(input_code['code'], user_to_email.id, datetime.utcnow() + timedelta(hours=1))
            db.session.add(pass_reset)
            db.session.commit()
        return render_template('forgot_password.html', form=None)
    # show form on page to put in email
    else:
        return render_template('forgot_password.html', form=RecoverPassword())

# necessary helper func for 
# putting mail on a queue
# with app context
def queue_mail(msg):
    with app.app_context():
        msg.send()

@app.route('/password_reset/<string:hashed_val>', methods=['GET', 'POST'])
def process_reset(hashed_val):
    s = URLSafeSerializer(app.config['SECRET_KEY'])
    if request.method == 'GET':
        # get posted signed token unsign it and look up which user object
        # corresponding to the email it is, then pwd reset prompt
        try:
            return render_template('reset_password.html', form=ResetPassword(), hashed_val=hashed_val)
        except (BadSignature, SignatureExpired) as e:
            pass
    elif request.method == 'POST':
        reset_password = ResetPassword(request.form)
        if request.form and reset_password.validate_on_submit(): 
            if request.form['password'] == request.form['password_two']:
                unsigned_token = s.loads(hashed_val)
                pass_reset = password_reset.PasswordReset.query.filter_by(code=unsigned_token['code']).first()
                user = get_user_method(pass_reset.user_object_id)
                user.password = user.hash_password(request.form['password'])
                db.session.commit()
        return redirect('/login')
'''
view route methods
'''

@app.route('/', methods=['GET'])
def main_page():
    text_area = TextareaForm()
    return render_template('main.html', current_user=current_user, form=text_area)

@app.route('/about', methods=['GET'])
def about_page():
    # if a user is set in the context
    return render_template('about.html', current_user=current_user)

# display a hex with all its links
@app.route('/hex/<string:hex_object_id>', methods=['GET'])
def hex_view(hex_object_id):
    hex_object = get_hex_object_method(hex_object_id)
    hex_owner = user_object.UserObject.query.filter_by(id=hex_object.owner_id).first()
    hexlinks = link_object.LinkObject.query.filter_by(hex_object_id=hex_object_id)
    hex_object.ex_hex_owner = hex_owner
    hex_object.ex_hexlinks = hexlinks
    edit_hex_name_form = None
    create_user = None
    text_area_form = False
    logged_in_claim_hex = False
    enable_editing_controls = False

    # hex is owned by anon, anonymous user
    # display a form to claim ownership
    if app.config['ANON_USER_NAME'] == hex_owner.username:
        # user is not logged in
        if current_user.is_anonymous:
            create_user = CreateUser()
        # user is logged in
        else:
            create_user = None
            logged_in_claim_hex = True
    # hex is owned by someone
    else:

        # hex is owned by current user
        if not current_user.is_anonymous and current_user.id == hex_owner.id:
            edit_hex_name_form = RenameHex()
            text_area_form = TextareaForm()
            enable_editing_controls = True

    return render_template('hex.html', current_user=current_user, hex_object=hex_object, edit_hex_name_form=edit_hex_name_form, form=create_user, textarea_form=text_area_form, enable_editing_controls=enable_editing_controls, logged_in_claim_hex=logged_in_claim_hex)

# display a link
@app.route('/link/<string:link_object_id>', methods=['GET'])
def link_view(link_object_id):
    link_object = get_link_method(link_object_id)
    return render_template('link.html', current_user=current_user, link=link_object)

# display a user with all their hexes
@app.route('/user/<string:username>', methods=['GET'])
def user_view(username):
    hexlinks = {}
    user_object = get_user_by_name(username)
    if user_object and not username == app.config['ANON_USER_NAME']:
        hex_objects = list(hex_object.HexObject.query.filter_by(user_object_id=user_object.id))
        for hex_obj in hex_objects:
            links = link_object.LinkObject.query.filter_by(hex_object_id=hex_obj.id)
            hexlinks[hex_obj.id] = [link.url for link in links]

        email_form = None
        enable_editing_controls = False
        if current_user == user_object:
            email_form = InputEmail() if not current_user.email else None
            enable_editing_controls = True

        return render_template('user.html', current_user=current_user, username=username, hexes=hex_objects, hexlinks=hexlinks, enable_editing_controls=enable_editing_controls, email_form=email_form)
    else:
        abort(404)

@app.route('/terms', methods=['GET'])
def terms_view():
    return render_template('terms.html')

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
        the_petname_bits = petname.Generate(2, ".").split('.')

        name = 'hex-' + the_petname_bits[0] + '-' + rw.random_word() #+ '-' + str(binascii.hexlify(os.urandom(16)))[2:-1]
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
    return render_template('main.html', current_user=current_user, form=text_area)

@app.route('/internal/form_user_create', methods=['POST'])
def form_user_create():
    create_user = CreateUser(request.form)
    if request.form and create_user.validate_on_submit() and request.form['password'] == request.form['password_two']:
        created_user = post_user_method(request.form['username'], request.form['password'], app.config['USER_MAKER_NAME'])
        login_user(created_user)
    else:
        abort(500)
    return redirect(url_for('user_view', username=created_user.username))

#when a user needs to claim and they are logged in
@app.route('/internal/form_make_or_claim_user_and_claim_hex_logged_in/<string:hex_object_id>', methods=['POST'])
def form_claim_hex_logged_in(hex_object_id):
    # if the owner id is something other than the anon id, the hex is already
    # owned
    hex_obj = get_hex_object_method(hex_object_id)
    hex_already_owned = hex_obj.owner_id != app.config['ANON_USER_ID']
    if current_user.is_anonymous or hex_already_owned:
        return jsonify({"witty_message": "you crafty little turd. stay away from our internal stuff."})
    else:
        session_user_object = current_user
        hex_to_reassign = hex_obj
        hex_to_reassign.owner_id = session_user_object.id
        hex_to_reassign.user_object_id = session_user_object.id
        db.session.commit()
        return redirect(url_for('hex_view', hex_object_id=hex_object_id))

#when a user needs to claim + create an acct or login
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
                # log the user in
                login_user(session_user_object)
        elif request.form['password'] == request.form['password_two']:
            # create the user
            created_user = post_user_method(request.form['username'], request.form['password'], app.config['USER_MAKER_NAME'])
            # assign the hex to that user
            hex_to_reassign = get_hex_object_method(hex_object_id)
            hex_to_reassign.owner_id = created_user.id
            hex_to_reassign.user_object_id = created_user.id
            db.session.commit()
            # log the user in
            login_user(created_user)
        else:
            # tell user about failed hex claim
            flash('there was an error claiming this hex, you probably just need to try again')
        return redirect(url_for('hex_view', hex_object_id=hex_object_id))
    else:
        return redirect(url_for('hex_view', hex_object_id=hex_object_id))

@app.route('/internal/form_add_links_to_hex/<string:hex_object_id>', methods=['POST'])
def form_add_links_to_hex(hex_object_id):
    is_hex_owner = current_user.id == get_hex_object_method(hex_object_id).owner_id

    if current_user.is_anonymous or not is_hex_owner:
        return jsonify({"witty_message": "you crafty little turd. stay away from our internal stuff."})
    else:
        text_area = TextareaForm(request.form)
        if is_hex_owner and request.form and text_area.validate_on_submit():
            submitted_urls = get_urls_from_blob(request.form['links'])
            for url in submitted_urls:
                post_link_method(url, '', hex_object_id)
            return redirect(url_for('hex_view', hex_object_id=hex_object_id))
        else:
            flash('there was an error adding links to this hex, reload and try again?')
            return redirect(url_for('hex_view', hex_object_id=hex_object_id))

@app.route('/internal/emailstore', methods=['POST'])
def store_email():
    if current_user.is_anonymous:
        return jsonify({"witty_message": "you crafty little turd. stay away from our internal stuff."})
    else:
        email_form = InputEmail(request.form)
        if request.form and email_form.validate_on_submit():
            if request.form['email'] == request.form['email_two']:
                user_object = get_user_method(current_user.id)
                user_object.email = request.form['email']
                db.session.commit()
        return redirect(url_for('user_view', username=current_user.username))

@app.route('/internal/form_update_hex_name/<string:hex_object_id>', methods=['POST'])
def update_hex_name(hex_object_id):
    is_hex_owner = current_user.id == get_hex_object_method(hex_object_id).owner_id

    if current_user.is_anonymous or not is_hex_owner:
        return jsonify({"witty_message": "you crafty little turd. stay away from our internal stuff."})
    else:
        rename_hex = RenameHex(request.form)
        if is_hex_owner and request.form and rename_hex.validate_on_submit():
            hex_to_update = get_hex_object_method(hex_object_id)
            hex_to_update.name = request.form['hexname']
            db.session.commit()
        return redirect(url_for('hex_view', hex_object_id=hex_object_id))

@app.route('/internal/form_update_link_description/<string:link_object_id>', methods=['POST'])
def update_link_description(link_object_id):
    is_link_owner = current_user.id == get_hex_object_method(get_link_method(link_object_id).hex_object_id).owner_id
    
    if current_user.is_anonymous or not is_link_owner:
        return jsonify({"witty_message": "you crafty little turd. stay away from our internal stuff."})
    else:
        rename_link = RenameLink(request.form)
        if is_link_owner and request.form and rename_link.validate_on_submit():
            link_to_update = get_link_method(link_object_id)
            link_to_update.name = request.form['linkdescription']
            db.session.commit()
        return redirect(url_for('hex_view', hex_object_id=hex_object_id))

@app.route('/internal/form_delete_hex/<string:hex_object_id>', methods=['POST'])
def internal_delete_hex(hex_object_id):
    is_hex_owner = current_user.id == get_hex_object_method(hex_object_id).owner_id
    
    if current_user.is_anonymous or not is_hex_owner:
        return jsonify({"witty_message": "you crafty little turd. stay away from our internal stuff."})
    else:
        hex_owner = get_user_method(get_hex_object_method(hex_object_id).owner_id)
        if is_hex_owner:
            delete_hex_method(hex_object_id)
        # return dummy json to ajax
        return jsonify({'success':'success'}), 200

@app.route('/internal/form_delete_link/<string:link_object_id>', methods=['POST'])
def internal_delete_link(link_object_id):
    link_to_delete = get_link_method(link_object_id)
    hex = get_hex_object_method(link_to_delete.hex_object_id)
    is_link_owner = current_user.id == get_hex_object_method(get_link_method(link_object_id).hex_object_id).owner_id
    
    if current_user.is_anonymous or not is_link_owner:
        return jsonify({"witty_message": "you crafty little turd. stay away from our internal stuff."})
    else:
        if is_link_owner:
            delete_link_method(link_object_id)
        # return dummy json to ajax
        return jsonify({'success':'success'}), 200

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
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, request.json, request.method):
        name = request.json.get('name')
        user_id = request.json.get('user_id')
        owner_id = request.json.get('owner_id')
        image_path = request.json.get('image_path')

        #create new hex
        if name is None or user_id is None or owner_id is None or image_path is None:
            abort(400)

        new_hex_object = post_hex_object_method(name, owner_id, user_id, image_path)
        return jsonify({'id':new_hex_object.id, 'name':new_hex_object.name, 'image_path':new_hex_object.image_path, 'owner_id':new_hex_object.owner_id, 'user_id':new_hex_object.user_object_id}), 201
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def post_hex_object_method(name, owner_id, user_id, image_path):
    new_hex_object = hex_object.HexObject(name, owner_id, user_id, image_path)
    db.session.add(new_hex_object)
    db.session.commit()
    return new_hex_object

@app.route('/api/v1.0/hex/<string:hex_object_id>', methods=['DELETE'])
@auth.login_required
def delete_hex(hex_object_id):
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, {"id":hex_object_id}, request.method):
        hex_object_delete = delete_hex_method(hex_object_id)
        return  jsonify({'id':hex_object_delete.id, 'name':hex_object_delete.name, 'image_path':hex_object_delete.image_path, 'owner_id':hex_object_delete.owner_id, 'user_id':hex_object_delete.user_object_id}), 200
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

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

def get_user_by_email(email):
    return user_object.UserObject.query.filter_by(email=email).first()

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
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, {"id":link_object_id}, request.method):
        retrieved_link = get_link_method(link_object_id)
        if retrieved_link:
            return jsonify({'id': retrieved_link.id, 'url': retrieved_link.url,'description': retrieved_link.description,'hex_object_id': retrieved_link.hex_object_id}), 200
        else:
            return jsonify({'error': 'we couldn\'t find that link, u must be wrong', 'code': 404}), 404
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

@app.route('/api/v1.0/hexlinks/<string:hex_object_id>', methods=['GET'])
@auth.login_required
def get_hexlinks(hex_object_id):
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, {"id":hex_object_id}, request.method):
        return_links = link_object.LinkObject.query.filter_by(hex_object_id=hex_object_id)
        if return_links:
            return jsonify({'hexlinks': [{'id': retrieved_link.id, 'url': retrieved_link.url,'description': retrieved_link.description,'hex_object_id': retrieved_link.hex_object_id} for retrieved_link in return_links]}), 200
        else:
            return jsonify({'error': 'we couldn\'t find those links, u must be wrong', 'code': 404}), 404
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def get_link_method(link_object_id):
    return link_object.LinkObject.query.filter_by(id=link_object_id).first()

#accepts multiple urls, so a list
@app.route('/api/v1.0/link', methods=['POST'])
@auth.login_required
def post_link():
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, request.json, request.method):
        url =  request.json.get('url')
        description =  request.json.get('description')
        hex_object_id =  request.json.get('hex_object_id')
        if url is None or hex_object_id is None:
            abort(400)
        new_link_object = post_link_method(url, description, hex_object_id)
        return jsonify({'id': new_link_object.id, 'urls': new_link_object.url,'description': new_link_object.description,'hex_object_id': new_link_object.hex_object_id}), 201
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

#accepts multiple urls, so a list
@app.route('/api/v1.0/hexlinks', methods=['POST'])
@auth.login_required
def post_hexlinks():
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, request.json, request.method):
        return_links = []
        for link in request.json:
            url = link.get('url')
            description = link.get('description')
            hex_object_id = link.get('hex_object_id')
            if url is None or hex_object_id is None:
                abort(400)
            new_link_object = post_link_method(url, description, hex_object_id)
            return_links.append(new_link_object)
        return jsonify({i:{'id': new_link_object.id, 'urls': new_link_object.url,'description': new_link_object.description,'hex_object_id': new_link_object.hex_object_id} for i, new_link_object in enumerate(return_links)}), 201
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def post_link_method(url, description, hex_object_id):
    url_parsed = urlparse(url)
    if url_parsed.scheme == '':
        if url_parsed.netloc.startswith('//'):
            url = 'http:' + url
        else:
            url = 'http://' + url
    new_link_object = link_object.LinkObject(url, description, hex_object_id)
    db.session.add(new_link_object)
    db.session.commit()
    j = q.enqueue(add_web_page_title_to_link, new_link_object.id, new_link_object.url)
    return new_link_object

@app.route('/api/v1.0/link/<string:link_object_id>', methods=['DELETE'])
@auth.login_required
def delete_link(link_object_id):
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, {"id":link_object_id}, request.method):
        delete_link = delete_link_method(link_object_id)
        return jsonify({'id': delete_link.id, 'url': delete_link.url,'description': delete_link.description,'hex_object_id': delete_link.hex_object_id}), 200
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

@app.route('/api/v1.0/hexlinks/<string:hex_object_id>', methods=['DELETE'])
@auth.login_required
def delete_hexlinks(hex_object_id):
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, {"id":hex_object_id}, request.method):
        delete_links = []
        return_links = link_object.LinkObject.query.filter_by(hex_object_id=hex_object_id)
        for link in return_links:
            delete_links.append(delete_link_method(link.id))
        return jsonify({'hexlinks': [{'id': delete_link.id, 'url': delete_link.url,'description': delete_link.description,'hex_object_id': delete_link.hex_object_id} for delete_link in delete_links]}), 200
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def delete_link_method(link_object_id):
    delete_link = link_object.LinkObject.query.filter_by(id=link_object_id).first()
    db.session.delete(delete_link)
    db.session.commit()
    return delete_link

@app.route('/api/v1.0/location', methods=['GET'])
@auth.login_required
def get_location():
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, request.json, request.method):
        hex_object_id = request.json.get('hex_object_id')
        user_object_id = request.json.get('user_object_id')
        return_location = get_location_method(user_object_id, hex_object_id)
        if return_location:
            return jsonify({'id': return_location.id,'user_object_id': return_location.user_object_id,'hex_object_id': return_location.hex_object_id, 'location': return_location.location}), 200
        else:
            return jsonify({'error': 'we couldn\'t find that location, u must be wrong', 'code': 404}), 404
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def get_location_method(user_object_id, hex_object_id):
    return ios_hex_location.IosHexLocation.query.filter_by(user_object_id=user_object_id, hex_object_id=hex_object_id).first()

def get_location_by_id(location_object_id):
    return ios_hex_location.IosHexLocation.query.filter_by(id=location_object_id).first()

@app.route('/api/v1.0/location', methods=['POST'])
@auth.login_required
def post_location():
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, request.json, request.method):
        platform = request.json.get('platform')
        location = request.json.get('location')
        user_object_id = request.json.get('user_object_id')
        hex_object_id = request.json.get('hex_object_id')
        if location is None or hex_object_id is None or platform is None:
            abort(400)
        if platform == 'ios':
            new_hex_location = post_location_method(user_object_id, hex_object_id, location)
        else:
            abort(400)
        return jsonify({'id': new_hex_location.id,'user_object_id': new_hex_location.user_object_id,'hex_object_id': new_hex_location.hex_object_id, 'location': new_hex_location.location}), 201
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def post_location_method(user_object_id, hex_object_id, location):
    new_hex_location = ios_hex_location.IosHexLocation(user_object_id, hex_object_id, location)
    db.session.add(new_hex_location)
    db.session.commit()
    return new_hex_location

@app.route('/api/v1.0/location/<string:location_object_id>', methods=['DELETE'])
@auth.login_required
def delete_location(location_object_id):
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, {"id":location_object_id}, request.method):
        hex_location = delete_location_method(location_object_id)
        return jsonify({'id': hex_location.id,'user_object_id': hex_location.user_object_id,'hex_object_id': hex_location.hex_object_id, 'location': hex_location.location}), 200
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def delete_location_method(location_object_id):
    hex_location = ios_hex_location.IosHexLocation.query.filter_by(id=location_object_id).first()
    db.session.delete(hex_location)
    db.session.commit()
    return hex_location

@app.route('/api/v1.0/send/<string:send_object_id>', methods=['GET'])
@auth.login_required
def get_send(send_object_id):
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, {"id":send_object_id}, request.method):
        retrieved_send_object = get_send_method(send_object_id)
        if retrieved_send_object:
            return jsonify({'id': retrieved_send_object.id, 'sender_id': retrieved_send_object.sender_id, 'recipient_id': retrieved_send_object.recipient_id, 'hex_object_id':retrieved_send_object.hex_object_id}), 200
        else:
            return jsonify({'error': 'we couldn\'t find that send, u must be wrong', 'code': 404}), 404
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def get_send_method(send_object_id):
    return send_object.SendObject.query.filter_by(id=send_object_id).first()

@app.route('/api/v1.0/send', methods=['POST'])
@auth.login_required
def post_send():
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, request.json, request.method):
        sender_id = request.json.get('sender_id')
        recipient_id = request.json.get('recipient_id')
        hex_object_id = request.json.get('hex_object_id')
        if sender_id is None or recipient_id is None or hex_object_id is None:
            abort(400)
        new_send_object = post_send_method(sender_id, recipient_id, hex_object_id)
        return jsonify({'id':new_send_object.id, 'sender_id': new_send_object.sender_id, 'recipient_id': new_send_object.recipient_id, 'hex_object_id':new_send_object.hex_object_id}), 201
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def post_send_method(sender_id, recipient_id, hex_object_id):
    new_send_object = send_object.SendObject(sender_id, recipient_id, hex_object_id)
    db.session.add(new_send_object)
    db.session.commit()
    return new_send_object

@app.route('/api/v1.0/send/<string:send_object_id>', methods=['DELETE'])
@auth.login_required
def delete_send(send_object_id):
    authorizing_user = get_user_by_name(request.authorization.username)
    if user_can_perform_action(authorizing_user, request.url_rule, {"id":send_object_id}, request.method):
        send_object_delete = delete_send_method(send_object_id)
        return jsonify({'sender_id': send_object_delete.sender_id, 'recipient_id': send_object_delete.recipient_id, 'hex_object_id':send_object_delete.hex_object_id}), 200
    else:
        return jsonify({'error': 'you dont have the right to touch that, you didnt build that', 'code': 403}), 403

def delete_send_method(send_object_id):
    send_object_delete = send_object.SendObject.query.filter_by(id=send_object_id).first()
    db.session.delete(send_object_delete)
    db.session.commit()
    return send_object_delete

'''
supporting non route methods
'''
# this method checks that the accessing user owns the thing they are accessing
def user_can_perform_action(user, endpoint, data, method):
    # if user is anonymous, no permission granted

    #else check the endpoint
    endpoint_type = str(endpoint).split('/')[3]
    print(user, endpoint, data, method)
    if endpoint_type == 'send':
        if method in ('GET', 'DELETE'):
            send_object = get_send_method(data.get('id'))
            if user.id in (send_object.recipient_id, send_object.sender_id):
                return True
            else:
                return False
        elif method == 'POST':
            if user.id == data.get('sender_id'):
                return True
            else:
                return False
    elif endpoint_type == 'hex':
        if method == 'POST':
            if user.id == data.get('user_id') and user.id == data.get('owner_id'):
                return True
            else:
                return False
        elif method == 'DELETE':
            hex_obj = get_hex_object_method(data.get('id'))
            if hex_obj.owner_id == user.id:
                return True
            else:
                return False
    elif endpoint_type == 'location':
        if method == 'GET':
            location = get_location_method(data.get('user_object_id'), data.get('hex_object_id'))
            if user.id == location.user_object_id:
                return True
            else:
                return False
        elif method == 'POST':
            if user.id == data.get('user_object_id'):
                return True
            else:
                return False
        elif method == 'DELETE':
            print(data.get('id'))
            location = get_location_by_id(data.get('id'))
            if user.id == location.user_object_id:
                return True
            else:
                return False
    elif endpoint_type == 'hexlinks':
        if method == 'GET':
            hex_obj = get_hex_object_method(data.get('id'))
            if hex_obj.owner_id == user.id:
                return True
            else:
                return False
        elif method == 'POST':
            print([user.id == get_hex_object_method(link.get('hex_object_id')).owner_id for link in data])
            return all([user.id == get_hex_object_method(link.get('hex_object_id')).owner_id for link in data])
        elif method == 'DELETE':
            hex_obj = get_hex_object_method(data.get('id'))
            if hex_obj.owner_id == user.id:
                return True
            else:
                return False
    elif endpoint_type == 'link':
        if method == 'POST':
            hex_obj = get_hex_object_method(data.get('hex_object_id'))
            if hex_obj.owner_id == user.id:
                return True
            else:
                return False
        elif method == 'DELETE':
            hex_obj = get_hex_object_method(get_link_method(data.get('id')).hex_object_id)
            if hex_obj.owner_id == user.id:
                return True
            else:
                return False

# this method hould ONLY be queued on a worker process
def add_web_page_title_to_link(link_object_id, url):
    r = requests.get(url)
    if r.status_code == 200:
        try:
            raw_html_bytes = r.content.decode('utf-8')
            html = bs4.BeautifulSoup(raw_html_bytes, 'html.parser')
            new_title = html.title.text
        except UnicodeError:
            new_title = url
    else:
        new_title = url
    new_link_object = get_link_method(link_object_id)
    new_link_object.web_page_title = new_title
    db.session.commit()

# get the urls from a blob of text
def get_urls_from_blob(blob):
    WEB_URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
    submitted_urls = re.findall(WEB_URL_REGEX, blob)
    return submitted_urls

# this error handler only fires when DEBUG=False,
# so it only fires on our production server
# @app.errorhandler(500)
# def internal_error(error):
#     r = send_mail('yvanscher@gmail.com', app.config['MAILGUN_SENDER'], '500 server error', '\n'.join(traceback.format_stack()), None)
#     return jsonify({'error': 'there was some terrible error, an email is on its way to us, don\'t fret little human', 'code': 500}), 500

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
'''