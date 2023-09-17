from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Random.random import StrongRandom
import re, base64, uuid
from flask_mysqldb import MySQL

class Utils:
    def __init__(self, mysql):
        self.mysql = mysql

    #---------------------------------------------------------------------------
    def generate_salt(self):
        return format(StrongRandom().getrandbits(256), 'x')

    #---------------------------------------------------------------------------
    def generate_password_hash(self, password, salt):
        raw = PBKDF2(password, salt, 32, 10000, None)
        return ''.join([format(b, '02x') for b in raw])

    #---------------------------------------------------------------------------
    def user_whitelist(self, value):
        if re.match("^[A-Za-z0-9_-]*$", value):
            return True
        else:
            return False

    #---------------------------------------------------------------------------
    def password_policy(self, password, username):
        if(len(password) < 8):
            print("password is too short")
            return False

        similarity = 0
        pc = password
        for c in username:
            i = pc.find(c)
            if(i != -1):
                similarity += 1
                pc = pc[:i] + pc[i+1:]

        similarity = similarity * 1.0 / len(username)
        if(similarity > 0.8):
            print("password is too similar to username")
            return False

        strength = 0
        if(re.match("^.*[A-Z].*$", password, re.UNICODE)):
            strength += 1
        if(re.match("^.*[a-z].*$", password, re.UNICODE)):
            strength += 1
        if(re.match("^.*[0-9].*$", password, re.UNICODE)):
            strength += 1
        if(re.match("^.*[^A-Za-z0-9].*$", password, re.UNICODE)):
            strength += 1
        print("password strength is", strength)
        return (strength > 2)

    #---------------------------------------------------------------------------
    def generate_csrf_token(self):
        return base64.b64encode(uuid.uuid4().hex.encode("ascii"))

    #---------------------------------------------------------------------------
    def store_user(self, user_name, password):
        salt = self.generate_salt()
        # could also be done in SQL using SHA2(msg,256)
        password_hash = self.generate_password_hash(password, salt)
        cur = self.mysql.connection.cursor()
        params = {'username': user_name,
                  'password_hash': password_hash,
                  'password_salt': salt
                  }
        cur.execute(
            "INSERT INTO user(username,password_hash,password_salt) "
            "  VALUES (%(username)s,%(password_hash)s,%(password_salt)s);",
            params)
        self.mysql.connection.commit()

    #---------------------------------------------------------------------------
    def check_cookie(self, cookie_val):
        print("checking cookie")
        cur = self.mysql.connection.cursor()
        params = {'session_id': cookie_val,
                  }
        # check if cookie session exists
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

    #---------------------------------------------------------------------------
    def check_password(self, user_name, password):
        cur = self.mysql.connection.cursor()

        # get users password hash and password salt
        cur.execute(
            "SELECT password_hash, password_salt FROM user "
            "  WHERE username = '%s';" %(user_name)
        )

        rv = cur.fetchall()

        if(rv):
            assert(len(rv[0]) == 2)
            # and recalculation is successful, return True
            return self.generate_password_hash(password, rv[0][1]) == rv[0][0]
        return False

    #---------------------------------------------------------------------------
    def create_and_store_session_id(self, username):
        session_id = uuid.uuid4()
        cur = self.mysql.connection.cursor()
        csrf_token = self.generate_csrf_token()
        username = username.split("'")[0]; # some additional SQLI protetection
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
        return (session_id,csrf_token)

    #---------------------------------------------------------------------------
    def remove_session(self, user_name):
        cur = self.mysql.connection.cursor()
        params = {'username': user_name}
        cur.execute("SELECT id FROM user WHERE username = %(username)s;", params)
        rv = cur.fetchall()
        if (len(rv) == 0): return
        params = {'uid': rv[0][0]}
        cur.execute("DELETE FROM session WHERE user_id = %(uid)s", params)
        self.mysql.connection.commit()

    #---------------------------------------------------------------------------
    def update_user(self, user):
        stmt = "UPDATE user SET role = 'admin' WHERE username = %(user)s;"
        params = {'user': user}
        cur = self.mysql.connection.cursor()
        cur.execute(stmt, params)
        self.mysql.connection.commit()
