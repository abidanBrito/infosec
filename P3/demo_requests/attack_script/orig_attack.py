#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def main():
    url = "http://localhost:80"
    s = requests.Session()
    data = {'username': "infosec", 'password': "SecretPW123"}
    r= s.post(url + "/login", data=data)
    index = str(r.text).find("InfoSec{")
    index2 = str(r.text).find("}")
    print(str(r.text)[index:index2+1])

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
