from Handlers.BaseHandler import *
import json

class MIT100k(BaseHandler):
    def get(self,action=None):
    	if action=='p2':
	        referer = self.request.referer
	        self.set_secure_cookie('referral', referer)
	        self.render('mobile/mit.html', **self.params)
