from Handlers.BaseHandler import *
from Utils.Twat import *

import json
import logging



class LandingPage(BaseHandler):
    """ Home page, first page shown """
    def get(self, action=None):
        fetch_twitter()
        self.render('splash.html', **self.params)
