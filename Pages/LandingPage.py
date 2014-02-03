from google.appengine.api import memcache
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
            tweets = memcache.get('twitter')
            self.response.headers['Content-Type'] = "application/json"
            if tweets is not None:
                self.write(tweets)
                return
            else:
                tweets = json.dumps(fetch_twitter())
                memcache.add(key="twitter", value=tweets, time=3600)
                self.write(tweets)
                return
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
        elif action=='music':
            self.params['seodir'] = 'music'
            self.params['seosub'] = 'instruments'
            self.params['items'] = 'Instruments'
            self.render('landing/music.html', **self.params)
        elif action=='biz':
            self.params['seodir'] = 'biz'
            self.params['seosub'] = 'shipments'
            self.params['items'] = 'stuff'
            self.render('landing/biz.html', **self.params)
        elif action=='event':
            self.params['seodir'] = 'event'
            self.params['seosub'] = 'shipments'
            self.params['items'] = 'stuff'
            self.render('landing/event.html', **self.params)
        elif action=='auto':
            self.params['seodir'] = 'auto'
            self.params['seosub'] = 'shipments'
            self.params['items'] = 'Auto parts'
            self.render('landing/auto.html', **self.params)

class CouponPage(BaseHandler):
    def get(self, action=None):
        if action=='gen':
            self.render('landing/coupongen.html', **self.params)
        else:
            c = Codes.by_code(action.upper())
            if not c:
                self.redirect('/')
            self.params['bizname'] = c.name
            c.views = c.views+1
            c.put()
            # set cookie so we know where they came from
            self.set_secure_cookie('code', action.upper())
            referer = self.request.referer
            self.set_secure_cookie('referral', referer)
            if c.category==0:
                self.redirect('/welcome/pets#coupon?'+c.name)
            elif c.category==1:
                self.redirect('/welcome/auto#coupon?'+c.name)
            elif c.category==2:
                self.redirect('/welcome/equip#coupon?'+c.name)
            elif c.category==3:
                self.redirect('/welcome/music#coupon?'+c.name)
            elif c.category==4:
                self.redirect('/welcome/event#coupon?'+c.name)
            else:
                self.redirect('/welcome/biz#coupon?'+c.name)

    def post(self, action=None):
        if action=='gen':
            name = self.request.get('name')
            cat = self.request.get('cat')
            # Look up code
            c = Codes.by_name(name.upper())
            if not c:
                c = Codes(name=name.upper(),category=int(cat))
                c.code = name[0:3].upper() + str(random.randint(0,99)) + 'FEB'
                c.put()
            self.params['last_biz'] = c.name
            self.params['last_code'] = c.code
            self.render('landing/coupongen.html', **self.params)
