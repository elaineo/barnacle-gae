from Handlers.BaseHandler import *
import json

class MIT100k(BaseHandler):
    def get(self,action=None):
    	if action=='p2':
	        referer = self.request.referer
	        self.set_secure_cookie('referral', referer)
	        self.redirect('/static/mobile/home.html')

class MobilePage(BaseHandler):
	# page to redirect mobile platforms to download app
	def get(self):
		self.render('mobile/index.html', **self.params)