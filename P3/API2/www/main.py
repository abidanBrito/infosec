from flask import Flask
from flask import request, redirect, abort
from flask import send_from_directory
from flask import render_template
from flask_mysqldb import MySQL
from string import Template
import threading
import string
import random
import time
from utils import Utils

#-------------------------------------------------------------------------------
INFOSEC_web = Flask(__name__)
INFOSEC_web.config['MYSQL_HOST'] = 'db'
INFOSEC_web.config['MYSQL_PORT'] = 3306
INFOSEC_web.config['MYSQL_USER'] = 'db_user'
INFOSEC_web.config['MYSQL_PASSWORD'] = 'Super_Secure_INFOSEC21_!?'
INFOSEC_web.config['MYSQL_DB'] = 'INFOSEC_DB'

mysql = MySQL(INFOSEC_web)
utils = Utils(mysql)
secure_random = random.SystemRandom()

#-------------------------------------------------------------------------------
@INFOSEC_web.route('/post', methods=['POST'])
def post():
    if ('session_id' in request.cookies):
        user = utils.check_cookie(request.cookies['session_id'])
        if (user is None):
            redirect_to_board = redirect('/')
            response = INFOSEC_web.make_response(redirect_to_board)
            return response
        params = request.form.to_dict()
        if utils.check_token(params['csrf_token'],request.cookies['csrf_token'] == False):
            redirect_to_board = redirect('/')
            response = INFOSEC_web.make_response(redirect_to_board)
            return response
        utils.insert_post_to_db(user["id"], params['content'])
        redirect_to_board = redirect('/logged_in')
        response = INFOSEC_web.make_response(redirect_to_board)
        return response
    else:
        redirect_to_board = redirect('/')
        response = INFOSEC_web.make_response(redirect_to_board)
        return response

#-------------------------------------------------------------------------------
@INFOSEC_web.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        params = request.form.to_dict()
        if 'csrf_token' in request.cookies:
            if utils.check_token(request.cookies['csrf_token'],params['csrf_token']):
                if ('session_id' in request.cookies):
                    session_id = request.cookies['session_id']
                    user = utils.check_cookie(session_id)
                    if (user is not None):
                        params = {"session_id": session_id, }
                        cur.execute("DELETE FROM session WHERE id = %(session_id)s", params)
                        mysql.connection.commit()

                    redirect_to_board = redirect('/')
                    response = INFOSEC_web.make_response(redirect_to_board)
                    response.delete_cookie('session_id')
                    response.delete_cookie('csrf_token')
                    return response
    return INFOSEC_web.send_static_file('index.html')

#-------------------------------------------------------------------------------
@INFOSEC_web.route('/register', methods=['GET', 'POST'])
def show_registration():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        params = request.form.to_dict()
        user_name = params['username']
        password = params['password']
        if user_name and utils.user_whitelist(user_name) and utils.password_policy(password, user_name):
            cur.execute("SELECT COUNT(*) FROM user u WHERE u.username=%s", (user_name,))
            rv = cur.fetchall()
            if rv[0][0] == 0:
                utils.store_user(user_name, password)
                return INFOSEC_web.send_static_file('index.html')
            else:
                # user already exists
                return INFOSEC_web.send_static_file('registration_failed.html')
        else:
            return INFOSEC_web.send_static_file('registration_failed.html')
    return INFOSEC_web.send_static_file('registration.html')

#-------------------------------------------------------------------------------
@INFOSEC_web.route('/logged_in', methods=['GET'])
def show_logged_in():
    if ('session_id' in request.cookies):
        user = utils.check_cookie(request.cookies['session_id'])
        if (user is None):
            redirect_to_board = redirect('/')
            response = INFOSEC_web.make_response(redirect_to_board)
            return response
        with open('./templates/logged_in.html', 'r') as f:
            HTML = f.read()
        messages = utils.print_posts()
        template = Template(HTML)
        flag = "No flag here..."
        if (user["role"] == "admin"):
            with open("flag.txt", 'r') as f:
                flag = f.readline().rstrip("\n")
        return template.substitute(user=utils.substitute_xss(user["username"]), csrf_token=request.cookies['csrf_token'], messages=messages, flag=flag)
    else:
        redirect_to_board = redirect('/')
        response = INFOSEC_web.make_response(redirect_to_board)
        return response

#-------------------------------------------------------------------------------
@INFOSEC_web.route('/get-account', methods=['GET'])
def show_account():
    if ('session_id' in request.cookies):
        user = utils.check_cookie(request.cookies['session_id'])
        if (user is None):
            redirect_to_board = redirect('/')
            response = INFOSEC_web.make_response(redirect_to_board)
            return response
        params = request.args.to_dict()
        if ('name' in params):
            account_details = utils.get_account(params['name'])
        else:
            account_details = utils.get_account("")
        return render_template('account.html', user_name=account_details["user_name"], user_id=account_details["user_id"], role=account_details["role"], last_login=account_details["last_login"])
    else:
        redirect_to_board = redirect('/')
        response = INFOSEC_web.make_response(redirect_to_board)
        return response

#-------------------------------------------------------------------------------
@INFOSEC_web.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        params = request.form.to_dict()
        user_name = params['username']
        password = params['password']
        if user_name and password:
            if utils.check_password(user_name, password):
                utils.remove_session(user_name)
                print("creating session...")
                session_id, csrf_token = utils.create_and_store_session_id(user_name)
                redirect_to_board = redirect('/logged_in')
                response = INFOSEC_web.make_response(redirect_to_board)
                response.set_cookie('session_id', value=str(session_id), httponly=True)# secure not possible (no HTTPS)
                response.set_cookie('csrf_token', value=str(csrf_token), httponly=True)# secure not possible (no HTTPS)
                return response
            else:
                return INFOSEC_web.send_static_file('login_failed.html')
        return INFOSEC_web.send_static_file('login_failed.html')
    else:
        return INFOSEC_web.send_static_file('index.html')

#-------------------------------------------------------------------------------
@INFOSEC_web.route('/')
def show_index():
    return INFOSEC_web.send_static_file('index.html')

#-------------------------------------------------------------------------------
@INFOSEC_web.after_request
def apply_csp(response):
    response.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self';"
    response.headers["X-XSS-Protection"] = "1"
    return response

#-------------------------------------------------------------------------------
def get_random_string(length):
    return ''.join(secure_random.choices(string.ascii_uppercase + string.digits, k = length))   

#-------------------------------------------------------------------------------
def beforeTasks():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user")
    mysql.connection.commit()
    prepareUsers()
    clear_sessions()

#-------------------------------------------------------------------------------
def clear_sessions():
    threading.Timer(300.0, clear_sessions).start()
    with INFOSEC_web.app_context():
        cur = mysql.connection.cursor()
        # remove sessions older than 10 minutes
        cur.execute("CALL purge_sessions(10);")
        print("removed old sessions")
        mysql.connection.commit()

#-------------------------------------------------------------------------------
def prepareUsers():
    random_index = secure_random.randint(0, 99)
    for index in range(100):
        if index == random_index:
            prepareAdmin()
            continue
        cur = mysql.connection.cursor()
        user_name = get_random_string(10)
        params = {'username': user_name }
        cur.execute("DELETE FROM user WHERE username = %(username)s", params)
        mysql.connection.commit()
        branch = secure_random.uniform(0,1) > 0.5
        if branch:
            utils.store_user(user_name, get_random_string(20), int(time.time() - secure_random.uniform(24 * 60 * 60 - 20, 24 * 60 * 60 + 20)))
        else:
            utils.store_user(user_name, get_random_string(20), int(time.time() - secure_random.uniform(0, 24 * 60 * 60 - 300)))
        if secure_random.uniform(0,1) > 0.95:
            utils.update_user(user_name)
        if branch:
            utils.insert_post_to_db(utils.get_account(user_name)["user_id"], get_random_string(10), int(time.time() - secure_random.uniform(10 * 60, 20 * 60)))
        else:
            utils.insert_post_to_db(utils.get_account(user_name)["user_id"], get_random_string(10), int(time.time() - secure_random.uniform(0, 10 * 60)))



#-------------------------------------------------------------------------------
def prepareAdmin():
    with open("admin.pw", 'r') as f:
        adminpw = f.read().rstrip("\n")

    cur = mysql.connection.cursor()
    user_name = get_random_string(10)
    params = {'username': user_name }
    cur.execute("DELETE FROM user WHERE username = %(username)s", params)
    mysql.connection.commit()
    utils.store_user(user_name, adminpw, time.time() - 60 * 60 * 24 + 3)
    utils.update_user(user_name)
    utils.create_and_store_session_id(user_name)
    utils.insert_post_to_db(utils.get_account(user_name)["user_id"], get_random_string(10) )

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    INFOSEC_web.before_first_request(beforeTasks)
    INFOSEC_web.run(host="0.0.0.0", port=8080)
