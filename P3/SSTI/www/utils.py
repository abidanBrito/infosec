import base64
import re
import uuid

from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Random.random import StrongRandom


class Utils:
    def __init__(self, mysql):
        self.mysql = mysql

    # ---------------------------------------------------------------------------
    def generate_salt(self):
        return format(StrongRandom().getrandbits(256), 'x')

    # ---------------------------------------------------------------------------
    def generate_password_hash(self, password, salt):
        raw = PBKDF2(password, salt, 32, 10000, None)
        return ''.join([format(b, '02x') for b in raw])

    # ---------------------------------------------------------------------------
    def generate_csrf_token(self):
        return base64.b64encode(uuid.uuid4().bytes)

    # ---------------------------------------------------------------------------
    def check_token(self, cookie, token):
        return (cookie == token)

    # ---------------------------------------------------------------------------
    def check_command_injection(self, s):
        blocked = ["popen", "run", "call", "check_call",
                   "check_output", "subprocess", "shell",
                   "os", "system", "communicate", "write", "import", "."]
        if any(substring in s for substring in blocked):
            return True
        return False

    # ---------------------------------------------------------------------------
    def store_reservation(self, name, number, guests, date, destination):
        cur = self.mysql.connection.cursor()
        params = {'name': name,
                  'number': number,
                  'guests': guests,
                  'date': date,
                  'destination': destination
                  }
        cur.execute(
            "INSERT INTO reservations(name, number, guests, date, destination) "
            "VALUES (%(name)s,%(number)s,%(guests)s,%(date)s,%(destination)s);",
            params)
        self.mysql.connection.commit()

    # ---------------------------------------------------------------------------
    def user_whitelist(self, value):
        if re.match("^[A-Za-z0-9_-]*$", value):
            return True
        else:
            return False

    # ---------------------------------------------------------------------------
    def password_policy(self, password, username):
        if len(password) < 8:
            print("password is too short")
            return False

        similarity = 0
        pc = password
        for c in username:
            i = pc.find(c)
            if i != -1:
                similarity += 1
                pc = pc[:i] + pc[i + 1:]

        similarity = similarity * 1.0 / len(username)
        if similarity > 0.8:
            print("password is too similar to username")
            return False

        strength = 0
        if re.match("^.*[A-Z].*$", password, re.UNICODE):
            strength += 1
        if re.match("^.*[a-z].*$", password, re.UNICODE):
            strength += 1
        if re.match("^.*[0-9].*$", password, re.UNICODE):
            strength += 1
        if re.match("^.*[^A-Za-z0-9].*$", password, re.UNICODE):
            strength += 1
        print("password strength is", strength)
        return strength > 2

    # ---------------------------------------------------------------------------
    def store_user(self, username, password, first_name, last_name):
        salt = self.generate_salt()
        password_hash = self.generate_password_hash(password, salt)
        cur = self.mysql.connection.cursor()
        params = {'username': username,
                  'password_hash': password_hash,
                  'password_salt': salt,
                  'first_name': first_name,
                  'last_name': last_name
                  }
        cur.execute(
            "INSERT INTO user(username,password_hash,password_salt,first_name,last_name) "
            "  VALUES (%(username)s,%(password_hash)s,%(password_salt)s,%(first_name)s,%(last_name)s);",
            params)
        self.mysql.connection.commit()

    # ---------------------------------------------------------------------------
    def check_password(self, username, password):
        cur = self.mysql.connection.cursor()
        params = {'username': username}

        cur.execute(
            "SELECT password_hash, password_salt FROM user "
            "  WHERE username = %(username)s;",
            params)

        rv = cur.fetchall()

        if rv and len(rv) == 1:
            assert len(rv[0]) == 2
            return self.generate_password_hash(password, rv[0][1]) == rv[0][0]
        return False

    # ---------------------------------------------------------------------------
    def remove_session(self, username):
        cur = self.mysql.connection.cursor()
        params = {'username': username}
        cur.execute(
            "SELECT id FROM user WHERE username = %(username)s;", params)
        rv = cur.fetchall()
        if len(rv) == 0:
            return
        params = {'uid': rv[0][0]}
        cur.execute("DELETE FROM session WHERE user_id = %(uid)s", params)
        self.mysql.connection.commit()

    # ---------------------------------------------------------------------------
    def create_and_store_session_id(self, username):
        session_id = uuid.uuid4()
        cur = self.mysql.connection.cursor()
        csrf_token = self.generate_csrf_token()
        params = {'username': username,
                  'csrf_token': csrf_token,
                  'session_id': session_id
                  }
        cur.execute(
            "INSERT INTO session(id,user_id,csrf_token) VALUES "
            "  (%(session_id)s,"
            "  (SELECT id FROM user WHERE username = %(username)s),%(csrf_token)s);",
            params)
        self.mysql.connection.commit()
        return (session_id, csrf_token)

    # ---------------------------------------------------------------------------
    def check_cookie(self, cookie_val):
        print("checking cookie")
        cur = self.mysql.connection.cursor()
        params = {'session_id': cookie_val,
                  }
        cur.execute("SELECT user_id, username, role FROM "
                    "  session INNER JOIN user ON(session.user_id=user.id) "
                    "  WHERE session.id = %(session_id)s", params)
        rv = cur.fetchall()
        if rv:
            cur.execute("UPDATE session SET timestamp = NOW() "
                        "WHERE id = %(session_id)s;", params)
            return {"id": rv[0][0], "username": rv[0][1], "role": rv[0][2]}
        else:
            return None

    # ---------------------------------------------------------------------------
    def update_user(self, user):
        params = {'username': user}
        stmt = "UPDATE user SET role = 'admin' WHERE username = %(username)s;"
        cur = self.mysql.connection.cursor()
        cur.execute(stmt, params)
        self.mysql.connection.commit()

    # ---------------------------------------------------------------------------
    def get_csp(self):
        SELF = '\'self\''
        csp = {
            'default-src': '\'none\'',
            'style-src': SELF,
            'script-src': SELF,
            'img-src': [SELF, 'data:'],
            'font-src': [SELF, 'data:'],
            'frame-src': 'https://www.google.com'
        }
        return csp
