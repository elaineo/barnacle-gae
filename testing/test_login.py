#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests import session
import json
import selenium
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


PORT = '8080'
DOMAIN = 'localhost'

def main ():
    # create account with fb
    with session() as c:
        d = { "id" : '123456',
                    "first_name" : 'Frëd',
                    "last_name" : 'Low',
                    "email" : 'fredlow340@yahoo.com',
                    "location" : 'Mountain View, CA' }
        headers = {'content-type': 'application/json; charset=utf-8json'}
        request = c.post('http://localhost:8080/signup/fb', data=json.dumps(d), headers=headers)

    with session() as c:
        d = { "id" : "123456",
                    "first_name" : "Frëd",
                    "last_name" : "Low",
                    "email" : "fredlow340@yahoo.com",
                    "location" : "Mountain View, CA"}
        headers = {'content-type': '; charset=utf-8'}
        request = c.post('http://localhost:8080/signup/fb', data=json.dumps(d), headers=headers)


    with session() as c:
        d = { "id" : "123",
                    "first_name" : "Frëd",
                    "last_name" : "Low",
                    "email" : "fredlow340@yahoo.com",
                    "location" : "Mountain View, CA"}
        headers = {'content-type': '; charset=utf-8json'}
        request = c.post('http://localhost:8080/signup/fb', data=json.dumps(d), headers=headers)


if __name__ == "__main__":
    main()
