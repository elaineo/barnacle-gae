from datetime import *
from Handlers.BaseHandler import *
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
            self.params['seosub'] = 'pets'
            self.params['items'] = 'Pet'
            self.render('landing/pets.html', **self.params)
        elif action=='equip':
            self.params['seosub'] = 'toys'
            self.params['items'] = 'Toys'
            self.render('landing/pets.html', **self.params)
        elif action=='biz':
            self.params['seosub'] = 'goods'
            self.params['items'] = 'stuff'
            self.render('landing/pets.html', **self.params)            
        elif action=='auto':
            self.params['seosub'] = 'goods'
            self.params['items'] = 'Auto parts'
            self.render('landing/pets.html', **self.params)            