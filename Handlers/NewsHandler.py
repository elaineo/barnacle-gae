from itertools import chain
from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import search

from Handlers.BaseHandler import *
from Models.Post.OfferRequest import *
from Models.User.Account import *
from Models.Post.Review import *
from Models.Tracker.TrackerModel import *

import json

# Stuff that should happen in the news feed:
#   Delivery status: tracking, completed - leave review
#   New reservations, New shit confirmed

class NewsHandler(BaseHandler):        
    def get(self, action=None):
        if action=='status':
            # find tracking information: return info about tracks
            self.response.headers['Content-Type'] = "application/json"
            tracks = []
            try:
                tm = TrackerModel.by_sender(self.user_prefs.key)
                for t in tm:
                    tracks.append(t.to_dict(True))
            except:
                return
            self.write(json.dumps(tracks))
        elif action=='reviews':
            # all completed deliveries should have a review
            try:
                # check to make sure completed
                exp = OfferRequest.by_user(self.user_prefs.key)
                exp = list(chain(exp, OfferRoute.by_user(self.user_prefs.key)))
            except:
                return
            needrevs = []
            for x in exp:
                r = Review.by_reservation(x.key, self.user_prefs.key)
                if not r:
                    review_url = '/review/'+x.key.urlsafe()+'?receiver='
                    if x.sender==self.user_prefs.key:
                        review_url = review_url + x.receiver.urlsafe()
                    else:
                        review_url = review_url + x.sender.urlsafe()
                    xdict = {'locend': x.locend, 
                            'review_url': review_url}
                    needrevs.append(xdict)
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(needrevs))