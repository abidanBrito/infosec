import os

from custom_jwt_lib import myjwt
from flask import Flask
from flask import request, redirect, render_template
from flask_talisman import Talisman
from functools import wraps

INFOSEC_web = Flask(__name__)
INFOSEC_web.secret_key = os.urandom(32).hex()

SELF = '\'self\''
csp = {
    'default-src': '\'none\'',
    'style-src': SELF,
    'script-src': SELF,
    'img-src': SELF,
    'font-src': SELF,
    'frame-src': 'https://www.google.com'
}
Talisman(INFOSEC_web,
         content_security_policy=csp,
         content_security_policy_nonce_in=['script-src', 'img-src'],
         force_https=False,
         session_cookie_secure=False,
         session_cookie_http_only=False,
         strict_transport_security=False)


class User():
    def __init__(self, id, name, password, is_admin):
        self.id = id
        self.name = name
        self.password = password
        self.is_admin = is_admin

    def get_json_dump(self):
        return {'id': self.id, 'name': self.name, 'is_admin': self.is_admin}


# This page is only for test visitors
users_list = [User(1, 'Visitor', 'WelcomePassword123', 'false')]

# -----------------------------------------------------------------------------
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # jwt is passed in the request header
        if 'jwt_token' in request.cookies:
            token = request.cookies['jwt_token']
        if not token:
            return INFOSEC_web.make_response('/')
        is_correct = False
        data = myjwt.decode(token)
        if data is not None and 'is_admin' in data:
            if data['is_admin'] == 'true':
                is_correct = True

        if is_correct:
            return f(True, *args, **kwargs)
        else:
            return INFOSEC_web.make_response('/')
    return decorated

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/index', methods=['GET'])
@INFOSEC_web.route('/', methods=['GET'])
def index():
    if 'jwt_token' in request.cookies:
        pubkey = open('keys/public-key.pem').read().strip()
        return render_template('index.html', user=users_list[0].name, pubkey=pubkey)
    else:
        return render_template('index.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/about', methods=['GET'])
def about():
    return render_template('about.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/flag', methods=['GET'])
@token_required
def flag(is_valid):
    if request.method == 'GET':
        with open('keys/flag.txt') as f:
            flag = f.read()
        return render_template('flag.html', flag=flag)

    return render_template('index.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/contact', methods=['GET'])
def contact():
    return render_template('contact.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/products', methods=['GET'])
def products():
    return render_template('products.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/single-product', methods=['GET'])
def single_product():
    return render_template('single_product.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        params = request.form.to_dict()
        user_name = params['username']
        password = params['password']
        if user_name and password:
            if user_name == users_list[0].name and password == users_list[0].password:
                # Generate jwt-token
                # We use RS256 as default
                token = myjwt.encode(
                    users_list[0].get_json_dump(), myjwt.RS256)
                response = INFOSEC_web.make_response(redirect('/index'))
                response.set_cookie('jwt_token', value=token, httponly=False)
                return response
            else:
                return render_template('login.html', login_failed=True)
        return render_template('login.html', login_failed=True)
    return render_template('login.html')


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    INFOSEC_web.run(host='0.0.0.0', port=8080)
