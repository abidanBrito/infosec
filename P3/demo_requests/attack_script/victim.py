#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By

def main():
    url = "http://localhost:80"


    options = webdriver.ChromeOptions()
    #options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    username = driver.find_element(By.NAME, "username")
    password = driver.find_element(By.NAME, "password")
    submit = driver.find_element(By.NAME, "login")

    print("Logging in...")

    input()
    username.send_keys("infosec")
    input()
    password.send_keys("SecretPW123")
    input()
    submit.click()
    input()
    driver.quit()


# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
