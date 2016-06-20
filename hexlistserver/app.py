'''
primary file with app logic
'''

import os
import re
import binascii
import requests
import traceback

from random_words import RandomWords
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


from hexlistserver.models import (hex_object, 
                                 link_object, 
                                 user_object, 
                                 ios_hex_location, 
                                 send_object)

from hexlistserver.forms.textarea import TextareaForm

'''
api route methods
'''

@app.route('/')
def main_page():
    text_area = TextareaForm()
    return render_template('main.html', user=None, form=text_area)

@app.route('/about')
def about_page():
    # if a user is set in the context
    return render_template('about.html')

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
        return jsonify({'id': retrieved_link.id, 'url': retrieved_link.url,'description': retrieved_link.description,'hex_object_id': retrieved_link.hex_object_id})
    else:
        return jsonify({'error': 'we couldn\'t find that link, u must be wrong', 'code': 404}), 404

def get_link_method(link_object_id):
    return link_object.LinkObject.query.filter_by(id=link_object_id).first()

#accepts multiple urls, so a list
@app.route('/api/v1.0/link', methods=['POST'])
@auth.login_required
def post_link():
    return_links = []
    print(request.json)
    for link in request.json.get('urls'):
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
non core methods
'''
@app.route('/internal/form_hex_create', methods=['POST'])
def form_hex_create():
    text_area = TextareaForm(request.form)
    if request.form and text_area.validate_on_submit():
        # get a list of links from the input field
        WEB_URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""
        submitted_urls = re.findall(WEB_URL_REGEX, request.form['links'])
        # create a user?
        # create info for new hex, attributed to te "anon" user
        rw = RandomWords()
        name = 'hex-' + rw.random_word() + '-' + str(binascii.hexlify(os.urandom(16)))[2:-1]
        if g and g.get('user_object'):
            user_id = g.user_object.id
            owner_id = g.user_object.id
        else:
            user_id = app.config['ANON_USER_ID']
            owner_id = app.config['ANON_USER_ID']
        image_path = ''

        #create new hex and new links
        new_hex_object = post_hex_object_method(name, owner_id, user_id, image_path)
        for url in submitted_urls:
            post_link_method(url, '', new_hex_object.id)
    return redirect('/')

'''
supporting non route methods
'''

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