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
        filter = None
        params = request.args.to_dict()
        if ('poster' in params):
            filter = params['poster']
        messages = utils.print_posts(filter)
        template = Template(HTML)
        return template.substitute(user=utils.substitute_xss(user["username"]), csrf_token=request.cookies['csrf_token'], messages=messages)
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
    prepareFlags()
    prepareAdmin()
    clear_sessions()

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
def prepareFlags():
    flag1 = ""
    flag2 = ""
    with open("flag1.txt", 'r') as f:
        flag1 = f.readline().rstrip("\n")
    with open("flag2.txt", 'r') as f:
        flag2 = f.readline().rstrip("\n")

    flag1 = flag1.replace("{","")
    flag1 = flag1.replace("}","")
    flag1 = flag1.replace("!", "$")

    INFOSEC_web.config['MYSQL_USER'] = 'root'
    INFOSEC_web.config['MYSQL_PASSWORD'] = 'secret'

    cur = mysql.connection.cursor()
    cur.execute("DROP TABLE IF EXISTS flag;")
    cur.execute("CREATE TABLE IF NOT EXISTS flag("
        "id INT NOT NULL AUTO_INCREMENT,"
        "" + flag1 + " VARCHAR(64) NOT NULL, PRIMARY KEY (id))"
        "ENCRYPTION='Y', ENGINE=InnoDB;")

    cur.execute("GRANT SELECT,INSERT,DELETE,UPDATE ON `INFOSEC_DB`.`flag` TO 'db_user'@'%';")
    cur.execute("FLUSH PRIVILEGES;")
    mysql.connection.commit()

    INFOSEC_web.config['MYSQL_USER'] = 'db_user'
    INFOSEC_web.config['MYSQL_PASSWORD'] = 'Super_Secure_INFOSEC21_!?'

    cur = mysql.connection.cursor()
    params = {'username': "flag_user"}
    cur.execute("DELETE FROM user WHERE username = %(username)s", params)
    mysql.connection.commit()
    utils.store_user("flag_user", flag2)

#-------------------------------------------------------------------------------
if __name__ == "__main__":
    INFOSEC_web.before_first_request(beforeTasks)
    INFOSEC_web.run(host="0.0.0.0", port=8080)
