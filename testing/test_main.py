#!/usr/bin/env python
# -*- coding: utf-8 -*-
from requests import session
import json
import selenium
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import re
import urllib


PORT = '8080'
DOMAIN = 'localhost'
HOST = 'http://localhost:8080'


def epoch_now():
    return time.mktime(time.gmtime())


def test_login_api ():
    # create account with fb
    with session() as c:
        d = { "id" : '123456',
                    "first_name" : 'Frëd',
                    "last_name" : 'Low',
                    "email" : 'fredlow340@yahoo.com',
                    "location" : 'Mountain View, CA' }
        headers = {'content-type': 'application/json; charset=utf-8json'}
        request = c.post('%s/signup/fb' % HOST, data=json.dumps(d), headers=headers)
        assert request.content == '{"status": "new"}'

    with session() as c:
        d = { "id" : "123456",
                    "first_name" : "Frëd",
                    "last_name" : "Low",
                    "email" : "fredlow340@yahoo.com",
                    "location" : "Mountain View, CA"}
        headers = {'content-type': '; charset=utf-8'}
        request = c.post('%s/signup/fb' % HOST, data=json.dumps(d), headers=headers)
        assert request.content == '{"status": "new"}'

    with session() as c:
        d = { "id" : "123",
                    "first_name" : "Frëd",
                    "last_name" : "Low",
                    "email" : "fredlow340@yahoo.com",
                    "location" : "Mountain View, CA"}
        headers = {'content-type': '; charset=utf-8json'}
        request = c.post('%s/signup/fb' % HOST, data=json.dumps(d), headers=headers)
        assert request.content == '{"status": "new"}'


def login(driver):
    # create account with fb
    driver.get(HOST)
    with session() as c:
        d = { "id" : '123456',
                    "first_name" : 'Frëd',
                    "last_name" : 'Low',
                    "email" : 'fredlow340@yahoo.com',
                    "location" : 'Mountain View, CA' }
        headers = {'content-type': 'application/json; charset=utf-8json'}
        request = c.post('%s/signup/fb' % HOST, data=json.dumps(d), headers=headers)
    for cookie in request.cookies:
        driver.add_cookie({'name' : cookie.name, 'value': cookie.value, 'path':'/', 'domain' : DOMAIN})
    return driver


def test_post_request():
    driver = webdriver.Firefox()
    driver = login(driver)
    driver.get(HOST)

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
    # click to next screen
    elem = driver.find_element_by_id('request_btn')
    elem.click()

    # do verification
    time.sleep(1)
    print driver.current_url
    assert driver.current_url == u'%s/request#' % HOST
    page_source = driver.page_source
    assert len(re.findall('San Francisco', page_source)) > 0
    assert len(re.findall('Los Angeles', page_source)) > 0
    elem = driver.find_element_by_name('items')
    elem.clear()
    elem.send_keys('mushrooms')
    elem = driver.find_element_by_name('rates')
    # agree to TOS
    elem = driver.find_element_by_id('tos')
    elem.click()
    # click to next screen
    elem = driver.find_element_by_id('request_btn')
    elem.click()
    # add credit card
    elem = driver.find_element_by_class_name('card-number')
    elem.send_keys('4242424242424242')
    elem = driver.find_element_by_class_name('cc-ey')
    elem.send_keys('14')
    elem = driver.find_element_by_class_name('cc-csc')
    elem.send_keys('123')
    elem = driver.find_element_by_id('request_btn')
    elem.click()

    # do verification or url
    time.sleep(1)
    target_pattern = u'%s/request/update/' % HOST
    assert len(re.findall(target_pattern, driver.current_url)) > 0

    driver.close()

def test_post_route():
    # create account with fb
    driver = webdriver.Firefox()
    driver = login(driver)
    driver.get(HOST)

    # navigate to post
    elem = driver.find_element_by_class_name('navicoroutes')
    elem.click()

    if driver.current_url == u'%s/drive' % HOST:
        elem = driver.find_element_by_tag_name('h1')
        if "Barnacle Profile" == elem.text:
            # need to fill out profile
            elem = driver.find_element_by_id('fillprof_btn')
            elem.click()

    # switch tabs to post route
    elem = driver.find_element_by_id('tab1')
    elem = elem.find_element_by_tag_name('a')
    elem.click()

    elem = driver.find_element_by_name('start')
    elem.send_keys('San Francisco, CA')

    elem = driver.find_element_by_name('dest')
    elem.send_keys('Los Angeles, CA')


    elem = driver.find_element_by_name('fbshare')
    elem.click()

    elem = driver.find_element_by_id('route_btn')
    elem.click()

    # do verification or url
    time.sleep(1)
    target_pattern = u'%s/route/[a-z]+' % HOST
    assert len(re.findall(target_pattern, driver.current_url)) > 0

    page_source = driver.page_source
    assert len(re.findall('San Francisco', page_source)) > 0
    assert len(re.findall('Los Angeles', page_source)) > 0

    driver.close()


if __name__ == "__main__":
    urllib.urlopen(HOST + '/debug/cities')
    #test_login_api()
    test_post_request()
    test_post_route()
