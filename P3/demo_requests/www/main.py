from flask import Flask
from flask import request, redirect, abort
from flask import send_from_directory
from flask_mysqldb import MySQL
from flask import render_template
import threading
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
        with open("flag.txt", 'r') as f:
            flag = f.readline().rstrip("\n")
        return render_template('logged_in.html', name=user["username"], flag=flag)
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
def beforeTasks():
    clear_sessions()
    prepareAdmin()

#-------------------------------------------------------------------------------
def clear_sessions():
    threading.Timer(60.0, clear_sessions).start()
    with INFOSEC_web.app_context():
        cur = mysql.connection.cursor()
        # remove sessions older than 10 minutes
        cur.execute("CALL purge_sessions(10);")
        print("removed old sessions")
        mysql.connection.commit()

#-------------------------------------------------------------------------------
def prepareAdmin():
    cur = mysql.connection.cursor()
    params = {'username': "infosec"}
    cur.execute("DELETE FROM user WHERE username = %(username)s", params)
    mysql.connection.commit()
    utils.store_user("infosec", "SecretPW123")
    utils.update_user("infosec")

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    INFOSEC_web.before_first_request(beforeTasks)
    INFOSEC_web.run(host="0.0.0.0", port=8080)
