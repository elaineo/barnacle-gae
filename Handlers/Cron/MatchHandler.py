from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import search

from Handlers.BaseHandler import *
from Models.RouteModel import *
from Models.RequestModel import *
from Utils.SearchUtils import *
from Utils.Defs import www_home
from Utils.Defs import request_note_sub
from Utils.EmailUtils import send_info
from Utils.DefsEmail import *

import json
dist = 100 #Arbitrary distance

class MatchHandler(BaseHandler):
    def day_ago(self):
        return datetime.now() - timedelta(1)
        
    def get(self, action=None):
        if action=='routes':
            routes = Route.query()
            drivers =[]
            for r in routes:
                matches = find_reqmatch(r)
                r.matches = matches
                if (True in [m.get().created > self.day_ago() for m in matches]):
                    drivers.append(r.userkey)
                r.put()
            drivers = list(set(drivers))
            logging.info(drivers)
            # go through the list and send notifications
            for d in drivers:
                if 3 in d.get().settings.notify:
                    self.__send_match2d(d)
        elif action=='requests':
            requests = Request.query()
            senders = []       
            for r in requests:
                matches = find_routematch(r)
                r.matches = matches
                if (True in [m.get().created > self.day_ago() for m in matches]):
                    senders.append(r.userkey)
                r.put()
            drivers = list(set(senders))
            logging.info(senders)
            # go through the list and send notifications
            for d in senders:
                if 3 in d.get().settings.notify:
                    self.__send_match2s(d)
        elif action=='matches':
            routecount = 0
            reqcount = 0
            try:
                # check routes
                routes = Route.by_userkey(self.user_prefs.key)            
                for r in routes:
                    routecount = routecount + len(r.matches)
                # check requests
                reqs = Request.by_userkey(self.user_prefs.key)            
                for r in reqs:
                    reqcount = reqcount + len(r.matches)
                rdump={'status':'ok'}
            except:
                rdump={'status':'fail'}
            rdump['routecount'] = routecount
            rdump['reqcount'] = reqcount
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(rdump))
                    
    def post(self, action=None):
        if action=='dumprequests':
            if not self.user_prefs:
                return
            # retrieve user's real location
            data = json.loads(self.request.body)
            logging.info(data)
            try:
                lat = data['startlat']
                lon = data['startlon']
                here = ndb.GeoPt(float(lat), float(lon))
            except:
                here = self.user_prefs.locpt
            # try:
            now = datetime.now().strftime('%Y-%m-%d')
            later = (datetime.now() + timedelta(365)).strftime('%Y-%m-%d')
            results = search_points_start(dist,'REQUEST_INDEX',later,now,'delivby','start',here)
            rdump = {'status':'ok'}
            rdump['count'] = len(results.results)
            rdump['link'] = '/search/request?startlat='+str(here.lat)+'&startlon='+str(here.lon)
            # except:
                # rdump = {'status':'fail'}
            self.response.headers['Content-Type'] = "application/json"                
            self.write(json.dumps(rdump))
            
    def __send_match2d(self, driver):
        routes = Route.by_userkey(driver)
        matches = []
        for r in routes:
            matches = matches + r.matches
        posts = []
        unroll=""
        for m in matches:
            p = m.get().to_search()
            if p['thumb_url'][0]=='/':
                p['thumb_url'] = www_home + p['thumb_url']                
            posts.append(p)
            unroll=unroll + "\n" + p['start'] + "\t" + p['dest'] + "\t" + p['delivby'] + "\t" + www_home + "/post/request/"+p['routekey']
        params = {'posts': posts}
        unrollparams = {'posts': unroll}
        self.send_match2d(driver.get().email, params, unrollparams)

    def __send_match2s(self,sender):
        reqs = Request.by_userkey(sender)
        matches = []
        for r in reqs:
            matches = matches + r.matches
        posts = []
        unroll=""
        for m in matches:
            p = m.get().to_search()
            if p['thumb_url'][0]=='/':
                p['thumb_url'] = www_home + p['thumb_url']                
            posts.append(p)
            unroll=unroll + "\n" + p['start'] + "\t" + p['dest'] + "\t" + p['delivend'] + "\t" + www_home + "/post/"+p['routekey']
        params = {'posts': posts}
        unrollparams = {'posts': unroll}
        self.send_match2s(sender.get().email, params, unrollparams)
        
    def send_match2d(self, email, params, unrollparams):
        htmlbody =  self.render_str('email/requestnote.html', **params)
        textbody = requestnote_txt % unrollparams
        send_info(to_email=email, subject=request_note_sub, 
            body=textbody, html=htmlbody)
            
    def send_match2s(self, email, params, unrollparams):
        htmlbody =  self.render_str('email/routenote.html', **params)
        textbody = routenote_txt % unrollparams
        send_info(to_email=email, subject=request_note_sub, 
            body=textbody, html=htmlbody)          
        
def find_reqmatch(route):
    # for a given route, get all matching requests
    pathpts, precision = RouteUtils().estPath(route.start, route.dest, dist)
    results = Request.search_route(pathpts, route.delivstart, route.delivend, precision)
    return [m.key for m in results]
    
def find_routematch(req):
    # for a given request, get all matching routes
    start = req.start
    dest = req.dest
    startresults = search_pathpts(dist,'ROUTE_INDEX',req.delivby.strftime('%Y-%m-%d'),'delivstart',start).results
    destresults = search_pathpts(dist,'ROUTE_INDEX',req.delivby.strftime('%Y-%m-%d'),'delivstart',dest).results
    results = search_intersect(startresults, destresults)
    keepers = []
    for c in results:
        startpt = field_byname(c, "start")
        dist0 = HaversinDist(start.lat,start.lon, startpt.latitude, startpt.longitude) 
        dist1 = HaversinDist(dest.lat,dest.lon, startpt.latitude, startpt.longitude)
        if dist0 < dist1:
            keepers.append(c)
    results = [k.doc_id for k in keepers]
    rkeys = []
    for r in results:
        if r.endswith('_RT'):
            rkeys.append(ndb.Key(urlsafe=r[:-3]))
        else:
            rkeys.append(ndb.Key(urlsafe=r))
    return rkeys