from Handlers.BaseHandler import *
from Utils.FacebookUtils import *
import json
import urlparse


class FBLoginPage(BaseHandler):
    """ Login to facebook account """
    def get(self):
        code = self.request.get('code')
        p = urlparse.urlparse(self.request.url)
        url = p.scheme + '://' + p.netloc + p.path
        url = 'http://www.gobarnacle.com:8080/fblogin'
        response = trade_code_for_access_token(url, code)
        if 'access_token' in response:
            access_token = response['access_token'][0]
            expire_time = response['expires'][0]
            debug_info = debug_token(access_token)
            if 'data' in debug_info and 'user_id' in debug_info['data']:
                user_id =  debug_info['data']['user_id']
                self.login(user_id, 'fb')
        self.redirect('/')
