from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Random.random import StrongRandom
import re, base64, uuid
from flask_mysqldb import MySQL
import time

class Utils:
    def __init__(self, mysql):
        self.mysql = mysql

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
        cur = self.mysql.connection.cursor()
        params = {'username': user_name,
                  'password': password
                  }
        cur.execute(
            "INSERT INTO user(username,password) "
            "  VALUES (%(username)s,%(password)s);",
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
        params = {'username': user_name}

        # get users password hash and password salt
        cur.execute(
            "SELECT password FROM user "
            "  WHERE username = %(username)s;",
            params)

        rv = cur.fetchall()

        # if only one user is selected
        if(rv and len(rv) == 1):
            assert(len(rv[0]) == 1)
            # and recalculation is successful, return True
            return password == rv[0][0]
        return False

    #---------------------------------------------------------------------------
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
    def check_token(self, cookie,token):
        return (cookie == token)

    #---------------------------------------------------------------------------
    def get_posts_from_db(self, filter):
        cur = self.mysql.connection.cursor()
        query = "SELECT p.timestamp,u.username,p.text FROM post p INNER JOIN user u ON p.user_id = u.id "
        if (filter):
            query += "WHERE u.username = '%s'" %(filter)
        cur.execute(query)
        return cur.fetchall()

    #---------------------------------------------------------------------------
    def print_posts(self, filter=None):
        posts = self.get_posts_from_db(filter)
        html = ""
        for i in range(0, len(posts)):
            html = html + "<tr><td>" + posts[i][0].strftime("%Y-%m-%d %H:%M:%S") + "</td><td>"
            html = html + self.substitute_xss(posts[i][1])
            html = html + "</td><td>" + self.substitute_xss(posts[i][2]) + "</td></tr>\n"
        return html

    #---------------------------------------------------------------------------
    def insert_post_to_db(self, user_id, message):
        if (not message): return
        cur = self.mysql.connection.cursor()
        params = {'user_id': user_id,
                  'text': message,
                  'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                  }
        cur.execute("INSERT INTO post(user_id,text,timestamp) "
                    "  VALUES (%(user_id)s,%(text)s,%(timestamp)s);", params)
        self.mysql.connection.commit()

    #---------------------------------------------------------------------------
    def substitute_xss(self, value):
        tmp = value.replace("&", "&amp;")
        tmp = tmp.replace("\"", "&quot;")
        tmp = tmp.replace("'", "&#039;")
        tmp = tmp.replace("<", "&lt;")
        return tmp.replace(">", "&gt;")

    #---------------------------------------------------------------------------
    def update_user(self, user):
        stmt = "UPDATE user SET role = 'admin' WHERE username = %(user)s;"
        params = {'user': user}
        cur = self.mysql.connection.cursor()
        cur.execute(stmt, params)
        self.mysql.connection.commit()
