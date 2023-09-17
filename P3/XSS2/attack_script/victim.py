#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import requests
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import time

def main():
    url = "http://localhost:8086"
    if (len(sys.argv) != 2):
        print("usage: " + sys.argv[0] + " <adminpwfile>")
        return
    with open(sys.argv[1], 'r') as f:
        adminpw = f.read().rstrip("\n")
    session = requests.Session()

    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url + "/logged_in")
    while True:
        session.post(url + "/login", {'username': 'admin', 'password': adminpw})
        for name, value in session.cookies.get_dict().items():
            driver.add_cookie({"name" : name, "value" : value})
        driver.get(url + "/logged_in")
        time.sleep(2)
    driver.quit()

# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
