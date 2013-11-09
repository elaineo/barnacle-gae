from Handlers.BaseHandler import *
from Utils.PageUtils import *
from Models.RequestModel import Request
import json

class LandingPage(BaseHandler):
    """ Home page, first page shown """
    def get(self):
        if self.user_prefs:
            nr = Request.newest(5)
            self.params['new_requests'] = [r.to_dict(incl_user=True) for r in nr]
            self.render('home.html', **self.params)
        else:
            self.render('splash.html', **self.params)
