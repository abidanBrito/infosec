import os
import threading

from flask import Flask, render_template, request, redirect, send_file
from flask_mysqldb import MySQL
from flask_talisman import Talisman

from utils import Utils

INFOSEC_web = Flask(__name__)
INFOSEC_web.secret_key = os.urandom(32).hex()

INFOSEC_web.config['MYSQL_HOST'] = 'db'
INFOSEC_web.config['MYSQL_PORT'] = 3306
INFOSEC_web.config['MYSQL_USER'] = 'db_user'
INFOSEC_web.config['MYSQL_PASSWORD'] = 'Super_Secure_INFOSEC22_!?'
INFOSEC_web.config['MYSQL_DB'] = 'INFOSEC_DB'
INFOSEC_web.config['CSV_FOLDER'] = 'files'

mysql = MySQL(INFOSEC_web)
utils = Utils(mysql)

Talisman(INFOSEC_web,
         content_security_policy=utils.get_csp(),
         content_security_policy_nonce_in=['script-src', 'img-src'],
         force_https=False,
         session_cookie_secure=False,
         session_cookie_http_only=False,
         strict_transport_security=False)

# -----------------------------------------------------------------------------


@INFOSEC_web.route('/index', methods=['GET'])
@INFOSEC_web.route('/', methods=['GET'])
def index():
    if 'session_id' in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            return render_template('index.html', logged_in_user=True)
    return render_template('login.html')

# -----------------------------------------------------------------------------


@INFOSEC_web.route('/login', methods=['GET', 'POST'])
def login():
    if 'session_id' in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            return INFOSEC_web.make_response(redirect('/'))

    if request.method == 'POST':
        params = request.form.to_dict()
        username = params['login_username']
        password = params['login_password']
        if username and password:
            if utils.check_password(username, password):
                utils.remove_session(username)
                print('creating session...')
                session_id, csrf_token = utils.create_and_store_session_id(
                    username)
                response = INFOSEC_web.make_response(redirect('/index'))
                response.set_cookie('session_id', value=str(session_id))
                response.set_cookie('csrf_token', value=str(csrf_token))
                return response
            else:
                return render_template('login.html', login_failed=True)
        return render_template('login.html', login_failed=True)

    return render_template('login.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/register', methods=['GET', 'POST'])
def register():
    if 'session_id' in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            return INFOSEC_web.make_response(redirect('/'))

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        params = request.form.to_dict()
        username = params['register_username']
        password = params['register_password']
        password_repeat = params['register_password_repeat']
        if username and password and utils.password_policy(password, username):
            cur.execute(
                'SELECT COUNT(*) FROM user u WHERE u.username=%s', (username,))
            rv = cur.fetchall()
            if rv[0][0] == 0:
                utils.store_user(username, password)
                return render_template('login.html')
            else:
                return render_template('register.html', user_already_exists=True)
        else:
            return render_template('register.html', registration_failed=True)

    return render_template('register.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        if 'csrf_token' in request.cookies and 'session_id' in request.cookies:
            session_id = request.cookies['session_id']
            user = utils.check_cookie(session_id)
            if user is not None:
                params = {'session_id': session_id, }
                cur.execute(
                    'DELETE FROM session WHERE id = %(session_id)s', params)
                mysql.connection.commit()

            response = INFOSEC_web.make_response(redirect('/'))
            response.delete_cookie('session_id')
            response.delete_cookie('csrf_token')
            return response

    return render_template('login.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/manage-users', methods=['GET'])
def manage_users():
    if 'session_id' in request.cookies:
        if (utils.check_cookie(request.cookies['session_id']) is not None):
            users = utils.get_user_data()
            return render_template('manage_users.html', users=users, logged_in_user=True)
    return render_template('login.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/edit/<int:uid>', methods=['GET', 'POST'])
def edit_user(uid: int):
    if 'session_id' in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is None:
            return INFOSEC_web.make_response(redirect('/'))

    if request.method == 'POST':
        params = request.form.to_dict()
        firstname = params['firstname']
        lastname = params['lastname']
        username = params['username']
        email = params['email']
        if uid and firstname and lastname and username and email:
            user = [uid, firstname, lastname, username, email]
            utils.update_user_data(user)
            utils.create_csv_file([user])

            users = utils.get_user_data()
            return render_template('manage_users.html', users=users, logged_in_user=True)
        else:
            user = utils.get_user_data(uid)
            return render_template('edit_users.html', user=user, logged_in_user=True)

    user = utils.get_user_data(uid)
    return render_template('edit_users.html', user=user, logged_in_user=True)

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/delete/<int:uid>', methods=['GET'])
def delete_user(uid: int):
    if 'session_id' in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            utils.delete_user(uid)
            users = utils.get_user_data()
            return render_template('manage_users.html', users=users, logged_in_user=True)
    return render_template('login.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/download', methods=['GET'])
def download_user():
    if 'session_id' in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            filename = request.args.get('filename')
            h = request.args.get('h')
            print(h)
            path = os.path.join(INFOSEC_web.config['CSV_FOLDER'], filename)
            print(path)
            if os.path.isfile(path):
                return send_file(path)
            else:
                users = utils.get_user_data()
                return render_template('manage_users.html', users=users, logged_in_user=True, error=True)
    return render_template('login.html')

# -------------------------------------------------------------------------------
def before_tasks():
    prepare_folder()
    clear_sessions()
    prepare_admin()
    create_dummy_data()

# -----------------------------------------------------------------------------
def create_dummy_data():
    user_data = [
        [1, 'John', 'Smith', 'smithj', 'smithj@infosec.at'],
        [2, 'Bill', 'Jones', 'jonesb', 'jonesb@infosec.at'],
        [3, 'Mary', 'James', 'jamesm', 'jamesm@infosec.at'],
        [4, 'Steve', 'Bride', 'brides', 'brides@infosec.at'],
        [5, 'Paul', 'Richard', 'richardp', 'richardp@infosec.at'],
        [6, 'Susan', 'Landi', 'landis', 'landis@infosec.at']
    ]
    for user in user_data:
        utils.populate(user[1], user[2], user[3], user[4])
        utils.create_csv_file([user])

# -------------------------------------------------------------------------------
def prepare_folder():
    if not os.path.exists(INFOSEC_web.config['CSV_FOLDER']):
        os.mkdir(INFOSEC_web.config['CSV_FOLDER'])

# -------------------------------------------------------------------------------
def clear_sessions():
    threading.Timer(60.0, clear_sessions).start()
    with INFOSEC_web.app_context():
        cur = mysql.connection.cursor()

        # remove sessions older than 10 minutes
        cur.execute('CALL purge_sessions(10);')
        print('removed old sessions')
        mysql.connection.commit()

# -------------------------------------------------------------------------------
def prepare_admin():
    with open('admin.pw', 'r') as f:
        adminpw = f.read().rstrip('\n')

    cur = mysql.connection.cursor()
    params = {'username': 'admin'}
    cur.execute('DELETE FROM user WHERE username = %(username)s', params)
    mysql.connection.commit()
    utils.store_user('admin', adminpw)
    utils.update_user('admin')


# -----------------------------------------------------------------------------
if __name__ == '__main__':
    INFOSEC_web.before_first_request(before_tasks)
    INFOSEC_web.run(host='0.0.0.0', port=8080)
