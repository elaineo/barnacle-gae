import urllib2
import requests
import urlparse
from google.appengine.api import urlfetch
import logging
import json


APP_ID = '540602052657989'
APP_SECRET = '89a554288210c8f7a8f3292612ed7a6f'


def login_url(redirect_uri):
    """ Generate a login url for Facebook"""
    url = 'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&response_type=%s&display=popup' % (APP_ID, redirect_uri, r'code')
    return url


def trade_code_for_access_token(redirect_uri, code):
    """ Trade code for access token for further calls """
    url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s' % (APP_ID, redirect_uri, APP_SECRET, code)
    r = urlfetch.fetch(url)
    d = urlparse.parse_qs(r.content)
    return d


def get_app_token():
    """ Get app token """
    url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials' % (APP_ID, APP_SECRET)
    r = urlfetch.fetch(url)
    d = urlparse.parse_qs(r.content)
    return d['access_token'][0]


def debug_token(token_to_inspect, app_token = get_app_token()):
    """ Examine the identity of the token
    """
    url = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s' % (token_to_inspect, app_token)
    r = urlfetch.fetch(url)
    return json.loads(r.content)
