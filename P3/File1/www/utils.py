import base64
import pickle
import re
import uuid

from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Random.random import StrongRandom
from xml.etree import ElementTree as et


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
        return cookie == token

    # ---------------------------------------------------------------------------
    def check_file_type(self, f):
        if not f.filename.endswith('.svg'):
            return False
        return True

    # ---------------------------------------------------------------------------
    def process_file(self, filename):
        with open('uploads/' + filename, 'rb') as f:
            tree = et.parse(f)
            root = tree.getroot()

            for svg_element in root:
                if "security_features" in svg_element.tag:
                    for att in svg_element.attrib:
                        try:
                            # Trying to parse the serialized security features.
                            # Only the newest tokens contain this feature.
                            if att == "security_code":
                                decode = base64.b64decode(svg_element.get(att))
                                content = pickle.loads(decode)
                                cur = self.mysql.connection.cursor()
                                params = {'name': filename,
                                          'tag': svg_element.tag,
                                          'content': content,
                                          'security_feature': True
                                          }
                                cur.execute(
                                    "INSERT INTO image(name,tag,content,security_feature) "
                                    "  VALUES (%(name)s,%(tag)s,%(content)s,%(security_feature)s);",
                                    params)
                                self.mysql.connection.commit()
                        except Exception as e:
                            print(e)
                else:
                    content = svg_element.attrib
                    cur = self.mysql.connection.cursor()
                    params = {'name': filename,
                              'tag': svg_element.tag,
                              'content': content,
                              'security_feature': False
                              }
                    cur.execute(
                        "INSERT INTO image(name,tag,content,security_feature) "
                        "  VALUES (%(name)s,%(tag)s,%(content)s,%(security_feature)s);",
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
    def store_user(self, username, password):
        salt = self.generate_salt()
        password_hash = self.generate_password_hash(password, salt)
        cur = self.mysql.connection.cursor()
        params = {'username': username,
                  'password_hash': password_hash,
                  'password_salt': salt
                  }
        cur.execute(
            "INSERT INTO user(username,password_hash,password_salt) "
            "  VALUES (%(username)s,%(password_hash)s,%(password_salt)s);",
            params)
        self.mysql.connection.commit()

    # ---------------------------------------------------------------------------
    def update_user(self, user):
        params = {'username': user}
        stmt = "UPDATE user SET role = 'admin' WHERE username = %(username)s;"
        cur = self.mysql.connection.cursor()
        cur.execute(stmt, params)
        self.mysql.connection.commit()

    # ---------------------------------------------------------------------------
    def check_password(self, username, password):
        cur = self.mysql.connection.cursor()
        params = {'username': username}

        # get users password hash and password salt
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
    def get_csp(self):
        SELF = '\'self\''
        csp = {
            'default-src': '\'none\'',
            'style-src': SELF,
            'script-src': SELF,
            'img-src': [SELF, 'data:'],
            'font-src': [SELF, 'data:']
        }
        return csp
