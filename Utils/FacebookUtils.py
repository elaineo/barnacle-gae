import urllib2
import requests
from google.appengine.api import urlfetch
import logging


APP_ID = '540602052657989'
APP_SECRET = '89a554288210c8f7a8f3292612ed7a6f'


def login_url(redirect_uri):
    url = 'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&response_type=%s&display=popup' % (APP_ID, redirect_uri, r'code')
    return url


def trade_code_for_access_token(redirect_uri, code):
    url = 'https://graph.facebook.com/oauth/access_token?client_id=%s&redirect_uri=%s&client_secret=%s&code=%s' % (APP_ID, redirect_uri, APP_SECRET, code)
    r = urlfetch.fetch(url)
    logging.info(r.content)
    return ''
