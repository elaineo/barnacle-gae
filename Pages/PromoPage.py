from Handlers.BaseHandler import *
from Utils.PageUtils import *
import json

class SpringBreak(BaseHandler):
    """ Spring Break page """
    def get(self):
        referer = self.request.referer
        self.set_secure_cookie('referral', referer)
        self.render('springbreak.html', **self.params)