from datetime import *
from Handlers.BaseHandler import *
from Models.Launch.CustModel import *
from Utils.Twat import *

import json
import logging

class LandingPage(BaseHandler):
    """ Home page, first page shown """
    def get(self, action=None):
        self.params['today'] = datetime.now().strftime('%Y-%m-%d')
        if action=='twitter':
            tweets = fetch_twitter()
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(tweets))
        elif action=='pets':
            self.params['seodir'] = 'pets'
            self.params['seosub'] = 'pets'
            self.params['items'] = 'Pet'
            self.render('landing/pets.html', **self.params)
        elif action=='equip':
            self.params['seodir'] = 'equip'
            self.params['seosub'] = 'toys'
            self.params['items'] = 'Toys'
            self.render('landing/equip.html', **self.params)
        # elif action=='biz':
            # self.params['seosub'] = 'goods'
            # self.params['items'] = 'stuff'
            # self.render('landing/biz.html', **self.params)            
        elif action=='auto':
            self.params['seodir'] = 'auto'
            self.params['seosub'] = 'goods'
            self.params['items'] = 'Auto parts'
            self.render('landing/auto.html', **self.params)            
            
class CouponPage(BaseHandler):            
    def get(self, action=None):
        if action=='gen':
            self.render('landing/coupongen.html', **self.params)  
        else: 
            c = Codes.by_code(action.upper())
            self.params['bizname'] = c.name
            if c.category==0:
                self.redirect('/welcome/pets#coupon?'+c.name)
            elif c.category==1:
                self.redirect('/welcome/auto#coupon?'+c.name)
            elif c.category==2:
                self.redirect('/welcome/equip#coupon?'+c.name)
            
    def post(self, action=None):
        if action=='gen':
            name = self.request.get('name')
            cat = self.request.get('cat')
            # Look up code
            c = Codes.by_name(name.upper())
            if not c:
                c = Codes(name=name.upper(),category=int(cat))
                c.put()
            self.params['last_biz'] = c.name
            self.params['last_code'] = c.code
            self.render('landing/coupongen.html', **self.params)  