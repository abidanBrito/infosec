#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:80"
    flag_regex = re.compile("(InfoSec{.+[^}]})")

    payload = {"username":"marv","password":"Asdf1234!"}

    r = requests.post(url + "/login",data=payload)
    print(r.text)


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass

