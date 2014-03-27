from google.appengine.ext import ndb

from Handlers.BaseHandler import *
from Models.Message import *
from Models.Post.Request import *
from Models.Post.Route import *
from Models.Post.Post import *
from Utils.SearchUtils import search_pathpts, search_todict, search_intersect, field_byname
from Utils.RouteUtils import *


import json
import logging
import urllib

        
class RRDashHandler(BaseHandler):
    def get(self, action=None, loc=None):
        if action=='matchdump':            
            reqdump = []
            requests = Request.query().order(-Request.created)
            for r in requests:
                if r.dead>0:
                    continue
                dump = r.to_dict()
                dump['key'] = r.key.urlsafe()
                if r.stats:
                    if r.stats.status > 10:
                        continue
                    dump['notes'] = r.stats.notes
                    dump['status'] = RequestStatus[r.stats.status]
                matches = []
                for q in r.matches:
                    try:
                        qq = q.get()
                        if qq.dead==0:
                            matches.append(qq.to_dict())
                    except:
                        continue
                dump['matches'] = matches
                reqdump.append(dump)  
            self.params['reqdump'] = reqdump
            self.render('search/reqs_matches.html', **self.params)

    
    def post(self, action=None):
        if action=='status':
            self.response.headers['Content-Type'] = "application/json"
            data = json.loads(unicode(self.request.body, errors='replace'))
            logging.info(data)
            key = data.get('key')
            if key:
                r=ndb.Key(urlsafe=key).get()
            status = data.get('status')
            if r.stats:
                r.stats.status = int(status)
            else:
                r.stats = ReqStats(status = int(status))
            r.put()