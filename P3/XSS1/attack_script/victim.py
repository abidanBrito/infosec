#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

def main():
    url = "http://localhost:8085"
    if (len(sys.argv) != 2):
        print("usage: " + sys.argv[0] + " [/path/to/flag]")
        return

    with open(sys.argv[1], 'r') as f:
        flag = f.readline().rstrip("\n")

    session = requests.Session()
    session.post(url + "/register", {'username': 'victim', 'password': 'Passw123'})
    cookies = session.cookies.update({'flag': flag})
    session.post(url + "/login", {'username': 'victim', 'password': 'Passw123'}, cookies=cookies)

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url + "/logged_in")
    for name, value in session.cookies.get_dict().items():
        driver.add_cookie({"name" : name, "value" : value})
    driver.get(url + "/logged_in")
    driver.quit()

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
