import twitter
from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Utils.Defs import twitter_handle

import json
import logging

class Twat(BaseHandler):
    def get(self):
        fetch_twitter(twitter_handle)
        self.render('test.html', **self.params)
        
def fetch_twitter(user):
    statuses = twitter.Api().GetUserTimeline(id=user, count=1)
    logging.info(statuses)
    s = statuses[0]
    #xhtml = TEMPLATE % (s.user.screen_name, s.text, s.user.screen_name, s.id, s.relative_created_at)
    