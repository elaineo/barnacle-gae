from Handlers.BaseHandler import *
from Utils.Twat import *

import json
import logging

class LandingPage(BaseHandler):
    """ Home page, first page shown """
    def get(self, action=None):
        if action=='twitter':
            tweets = fetch_twitter()
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(tweets))
        else:
            self.render('launch/landing.html', **self.params)
