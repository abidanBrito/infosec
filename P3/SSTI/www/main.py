import os
import threading

from flask import Flask, render_template, render_template_string, request, redirect
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
@INFOSEC_web.route('/', methods=['GET'])
@INFOSEC_web.route('/index', methods=['GET'])
def index():
    if "session_id" in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            return render_template("index.html", logged_in_user=True)
    return render_template("index.html")

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/about', methods=['GET'])
def about():
    if "session_id" in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            return render_template("about.html", logged_in_user=True)
    return render_template("about.html")

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/login', methods=['GET', 'POST'])
def login():
    if "session_id" in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            return INFOSEC_web.make_response(redirect('/'))

    if request.method == 'POST':
        params = request.form.to_dict()
        username = params['login_email']
        password = params['login_password']
        if username and password:
            if utils.check_password(username, password):
                utils.remove_session(username)
                print("creating session...")
                session_id, csrf_token = utils.create_and_store_session_id(
                    username)
                response = INFOSEC_web.make_response(redirect('/index'))
                response.set_cookie('session_id', value=str(session_id))
                response.set_cookie('csrf_token', value=str(csrf_token))
                return response
            else:
                return render_template("login.html", login_failed=True)
        return render_template("login.html", login_failed=True)

    return render_template("login.html")

# -----------------------------------------------------------------------------


@INFOSEC_web.route('/register', methods=['GET', 'POST'])
def register():
    if "session_id" in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            return INFOSEC_web.make_response(redirect('/'))

    if request.method == 'POST':
        cur = mysql.connection.cursor()
        params = request.form.to_dict()
        first_name = params['register_firstname']
        last_name = params['register_lastname']
        username = params['register_email']
        password = params['register_password']
        if username and password and utils.password_policy(password, username):
            cur.execute(
                "SELECT COUNT(*) FROM user u WHERE u.username=%s", (username,))
            rv = cur.fetchall()
            if rv[0][0] == 0:
                utils.store_user(username, password, first_name, last_name)
                return render_template("index.html")
            else:
                return render_template("register.html", user_already_exists=True)
        else:
            return render_template("register.html", registration_failed=True)

    return render_template("register.html")

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        cur = mysql.connection.cursor()

        if 'csrf_token' in request.cookies and 'session_id' in request.cookies:
            session_id = request.cookies['session_id']
            user = utils.check_cookie(session_id)
            if user is not None:
                params = {"session_id": session_id, }
                cur.execute(
                    "DELETE FROM session WHERE id = %(session_id)s", params)
                mysql.connection.commit()

            response = INFOSEC_web.make_response(redirect('/'))
            response.delete_cookie('session_id')
            response.delete_cookie('csrf_token')
            return response

    return render_template('index.html')

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/deals', methods=['GET'])
def deals():
    if request.method == 'GET':
        params = request.args.to_dict()

        if 'Location' in params and 'Price' in params:
            location = params['Location']
            if utils.check_command_injection(location):
                location = "Each City"
        else:
            location = "Each City"

        path = os.path.dirname(os.path.abspath(
            __file__)) + '/templates/deals.html'
        template = open(path).read()
        new_template = template.replace("TITLE_PLACEHOLDER", location)

        if "session_id" in request.cookies:
            if utils.check_cookie(request.cookies['session_id']) is not None:
                return render_template_string(new_template, logged_in_user=True)

        return render_template_string(new_template)

# -----------------------------------------------------------------------------
@INFOSEC_web.route('/reservation', methods=['GET', 'POST'])
def reservation():
    if "session_id" in request.cookies:
        if utils.check_cookie(request.cookies['session_id']) is not None:
            return render_template("reservation.html", logged_in_user=True)

    if request.method == 'POST':
        mysql.connection.cursor()
        params = request.form.to_dict()
        name = params['name']
        number = params['number']
        guests = params['guests']
        date = params['date']
        destination = params['destination']
        if name and number and guests and date and destination:
            utils.store_reservation(name, number, guests, date, destination)
            return render_template("index.html")
        else:
            return render_template("reservation.html")

    return render_template("reservation.html")

# -------------------------------------------------------------------------------
def before_tasks():
    clear_sessions()
    prepare_admin()

# -------------------------------------------------------------------------------
def clear_sessions():
    threading.Timer(60.0, clear_sessions).start()
    with INFOSEC_web.app_context():
        cur = mysql.connection.cursor()

        # remove sessions older than 10 minutes
        cur.execute("CALL purge_sessions(10);")
        print("removed old sessions")
        mysql.connection.commit()

# -------------------------------------------------------------------------------
def prepare_admin():
    with open("admin.pw", 'r') as f:
        adminpw = f.read().rstrip("\n")

    cur = mysql.connection.cursor()
    params = {'username': "admin@infosec.at"}
    cur.execute("DELETE FROM user WHERE username = %(username)s", params)
    mysql.connection.commit()
    utils.store_user("admin@infosec.at", adminpw, "admin", "admin")
    utils.update_user("admin@infosec.at")


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    INFOSEC_web.before_first_request(before_tasks)
    INFOSEC_web.run(host="0.0.0.0", port=8080)
