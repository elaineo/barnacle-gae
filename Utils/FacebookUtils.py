import urllib2
import requests
import urlparse
from google.appengine.api import urlfetch
import logging
import json


# 1) direct users to facebook login url with a redirect back
# 2) a code will be in the query string of redirected url
# 3) get the code from query parameter and trade for access_token on the backend
# 4) login in the user if acesss_token and debug_info correspond to user


APP_ID = '540602052657989'
APP_SECRET = '89a554288210c8f7a8f3292612ed7a6f'


def login_url(redirect_uri):
    """ Generate a login url for Facebook"""
    url = 'https://www.facebook.com/dialog/oauth?client_id=%s&redirect_uri=%s&response_type=%s&display=popup&scope=email,user_location' % (APP_ID, redirect_uri, r'code')
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

        Example API response
        {
            "data": {
                "app_id": 138483919580948,
                "application": "Social Cafe",
                "expires_at": 1352419328,
                "is_valid": true,
                "issued_at": 1347235328,
                "metadata": {
                    "sso": "iphone-safari"
                },
                "scopes": [
                    "email",
                    "publish_actions"
                ],
                "user_id": 1207059
            }
        }
    """
    url = 'https://graph.facebook.com/debug_token?input_token=%s&access_token=%s' % (token_to_inspect, app_token)
    r = urlfetch.fetch(url)
    return json.loads(r.content)

def collect_info(userid, access_token):
    url = 'https://graph.facebook.com/%s?fields=id,first_name,last_name,username,email,location&access_token=%s' % (userid, access_token)
    r = urlfetch.fetch(url)
    return json.loads(r.content)