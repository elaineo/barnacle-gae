from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import search

from Handlers.BaseHandler import *
from Models.Post.Route import *
from Models.Post.Request import *
from Models.Post.OfferRoute import *
from Models.Post.OfferRequest import *
from Models.Launch.CLModel import *
from Utils.SearchDocUtils import *
from Utils.SearchScraped import *
from Utils.SearchUtils import expire_pathpts

import json
import logging

class ExpireHandler(BaseHandler):
    def get(self):
        deaddump={}
        now = date.today()
        expire_pathpts(PATHPT_INDEX, now.strftime('%Y-%m-%d'), "delivend")
        deadroutes = Route.query(Route.delivend<now,Route.dead==0)
        route_index = search.Index(name=ROUTE_INDEX)
        for r in deadroutes:
            r.dead = PostStatus.index('EXPIRED')
            r.put()
            route_index.delete(r.key.urlsafe())
            if r.roundtrip:
                route_index.delete(r.key.urlsafe()+'_RT')

        deadreqs = Request.query(Request.delivby<now,Request.dead==0)
        req_index = search.Index(name=REQUEST_INDEX)
        for r in deadreqs:
            r.dead = PostStatus.index('EXPIRED')
            r.put()
            route_index.delete(r.key.urlsafe())
        # Orphan reservations
        deadres = OfferRequest.query(OfferRequest.deliverby<now,OfferRequest.dead==0) 
        for q in deadres:
            q.dead = PostStatus.index('EXPIRED')
            q.put()
        deadreq = OfferRoute.query(OfferRoute.deliverby<now, OfferRoute.dead==0) 
        for q in deadreq:
            q.dead = PostStatus.index('EXPIRED')
            q.put()            
        deadcl = CLModel.query().filter(CLModel.delivend<now)
        cl_index = search.Index(name=PATHPT_INDEX)
        bodycount = 0
        for r in deadcl:
            cl_index.delete(r.key.urlsafe())
            r.key.delete()
            bodycount=bodycount+1            
        logging.info(str(bodycount) + ' CL entries deleted')
        
        deadz = ZimModel.query().filter(ZimModel.delivend<now)
        z_index = search.Index(name=ZIM_INDEX)
        for r in deadz:
            z_index.delete(r.key.urlsafe())
            r.key.delete()
        
        hourago = datetime.now() - timedelta(minutes=60)
        deadsearch = SearchEntry.query().filter(SearchEntry.created < hourago)
        for s in deadsearch:
            s.key.delete()            
        return 