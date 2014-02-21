from datetime import *
from google.appengine.ext import ndb

from Handlers.BaseHandler import *
from Models.Launch.CLModel import *
from Utils.RouteUtils import *
from Utils.ValidUtils import *

class CLHandler(BaseHandler):
    def get(self, action=None,key=None):
        if action=='jsonroute' and key:
            try:
                route=ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return  
            rdump = RouteUtils.dumproute(route)
            self.response.headers['Content-Type'] = "application/json"
            self.write(rdump)
        elif key: # check if user logged in
            self.view_page(key)
        else:
            self.redirect('/search') 
            
    def view_page(self,key):
        try:
            p = ndb.Key(urlsafe=key).get()
            self.params.update(p.to_dict())
            self.render('launch/scraped.html', **self.params)
            return
        except:
            self.abort(409)
            return  
            