from flask import Flask
from flask import request, redirect, abort
from flask import send_from_directory
from flask_mysqldb import MySQL
from string import Template
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
@INFOSEC_web.route('/flags', methods=['GET', 'POST'])
def flags():
    if (request.method == 'GET'):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, flag FROM flags")
        posts =  cur.fetchall()
        flags = ""
        for i in range(0, len(posts)):
            flags = flags + "<tr><td>"
            flags = flags + str(posts[i][0])
            flags = flags + "</td><td>" + utils.substitute_xss(str(posts[i][1])) + "</td></tr>\n"
        with open('./templates/flags.html', 'r') as f:
            HTML = f.read()
        template = Template(HTML)
        return template.substitute('flags.html', flags=flags)

    if (request.method == 'POST'):
        redirect_to_board = redirect('/flags')
        response = INFOSEC_web.make_response(redirect_to_board)
        if ('flag' not in request.cookies):
            return response
        cur = mysql.connection.cursor()
        params = {'flag': request.cookies['flag']}
        cur.execute("INSERT INTO flags(flag) "
                    "  VALUES (%(flag)s);", params)
        mysql.connection.commit()
        return response
    return INFOSEC_web.send_static_file('index.html')

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
        template = Template(HTML)
        messages = utils.print_posts()
        return template.substitute(user=user["username"], csrf_token=request.cookies['csrf_token'], messages=messages)
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
                response.set_cookie('session_id', value=str(session_id))# secure not possible (no HTTPS)
                response.set_cookie('csrf_token', value=str(csrf_token))# secure not possible (no HTTPS)
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
    with open("admin.pw", 'r') as f:
        adminpw = f.read().rstrip("\n")

    cur = mysql.connection.cursor()
    params = {'username': "admin"}
    cur.execute("DELETE FROM user WHERE username = %(username)s", params)
    mysql.connection.commit()
    utils.store_user("admin", adminpw)
    utils.update_user("admin")

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    INFOSEC_web.before_first_request(beforeTasks)
    INFOSEC_web.run(host="0.0.0.0", port=8080)
