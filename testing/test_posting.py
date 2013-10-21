#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests import session
import json
import selenium
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re


PORT = '8080'
DOMAIN = 'localhost'


def main():
    # create account with fb
    with session() as c:
        d = { "id" : '123456',
                    "first_name" : 'Frëd',
                    "last_name" : 'Low',
                    "email" : 'fredlow340@yahoo.com',
                    "location" : 'Mountain View, CA' }
        headers = {'content-type': 'application/json; charset=utf-8json'}
        request = c.post('http://localhost:8080/signup/fb', data=json.dumps(d), headers=headers)

    driver = webdriver.Firefox()
    driver.get("http://127.0.0.1:8080/")
    driver.add_cookie({'name':'key', 'value':'value', 'path':'/'})
    for cookie in request.cookies:
        driver.add_cookie({'name' : cookie.name, 'value': cookie.value, 'path':'/', 'domain' : '127.0.0.1'})

    all_cookies = driver.get_cookies()

    driver.get("http://127.0.0.1:8080/")

    # navigate to post
    elem = driver.find_element_by_class_name('navicoreqs')
    elem.click()

    # enter information
    elem = driver.find_element_by_name('start')
    elem.clear()
    elem.send_keys('San Francisco, CA')
    elem = driver.find_element_by_name('dest')
    elem.clear()
    elem.send_keys('Los Angeles, CA')
    elem = driver.find_element_by_name('reqdate')
    elem.clear()
    elem.send_keys('10/24/2013')
    elem = driver.find_element_by_name('rates')
    elem.clear()
    elem.send_keys('10')
    elem = driver.find_element_by_id('cap0')
    elem.click()
    elem = driver.find_element_by_name('items')
    elem.clear()
    elem.send_keys('mushrooms')
    elem = driver.find_element_by_name('fbshare')
    elem.click()

    elem = driver.find_element_by_id('request_btn')
    elem.click()

    # do verification
    time.sleep(1)
    assert driver.current_url == u'http://127.0.0.1:8080/post/request'
    page_source = driver.page_source
    assert len(re.findall('San Francisco', page_source)) > 0
    assert len(re.findall('Los Angeles', page_source)) > 0
    assert len(re.findall('mushrooms', page_source)) > 0
    assert len(re.findall('\$10', page_source)) > 0

    driver.close()
    print 'Testing Done'


if __name__ == "__main__":
    main()
