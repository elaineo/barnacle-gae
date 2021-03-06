from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import search

from Handlers.BaseHandler import *
from Handlers.SearchHandler import search_requests
from Models.Post.Route import *
from Models.Post.Request import *
from Utils.SearchUtils import *
from Utils.data.EmailAddr import www_home
from Utils.EmailUtils import send_info
from Utils.Email.Match import *
from Utils.RouteUtils import *

import json
import logging
dist = 100 #Arbitrary distance

class MatchHandler(BaseHandler):
    def day_ago(self):
        return datetime.now() - timedelta(1)

    def get(self, action=None, key=None):
        if action=='routes':
            routes = Route.query(Route.dead==0)
            drivers =[]
            for r in routes:
                self.__updateroute(r)
                if (True in [m.get().created > self.day_ago() for m in r.matches]):
                    drivers.append(r.key.parent())
            drivers = list(set(drivers))
            # go through the list and send notifications
            for d in drivers:
                try:
                    if 3 in d.get().settings.notify:
                        self.__send_match2d(d)
                except:
                    continue
        elif action=='requests':
            requests = Request.query(Request.dead==0)
            senders = []
            for r in requests:
                self.__updatereq(r)
                # check for deleted matches
                try:
                    if (True in [m.get().created > self.day_ago() for m in r.matches]):
                        senders.append(r.key.parent())
                except:
                    pass
            senders = list(set(senders))
            # go through the list and send notifications
            for d in senders:
                try:
                    if 3 in d.get().settings.notify:
                        self.__send_match2s(d)
                except:
                    continue
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
        elif action=='updatereq' and key:
            r = ndb.Key(urlsafe=key).get()
            self.__updatereq(r)
        elif action=='updateroute' and key:
            r = ndb.Key(urlsafe=key).get()
            self.__updateroute(r)
        elif action=='cleanmatch' and key:
            # delete the key in matches
            r = ndb.Key(urlsafe=key).get()
            type = r.__class__.__name__
            if type=='Route':
                matches = Request.by_match(ndb.Key(urlsafe=key))
            else:
                matches = Route.by_match(ndb.Key(urlsafe=key))
            for m in matches:
                m.matches.remove(ndb.Key(urlsafe=key))
                m.put()
        elif action=='cleanmatches':
            requests = Request.query(Request.dead==0)
            for r in requests:
                r.matches=[]
                r.put()

    def post(self, action=None):
        if action=='dumprequests':
            if not self.user_prefs:
                return
            # retrieve user's real location
            data = json.loads(self.request.body)
            try:
                lat = data['startlat']
                lon = data['startlon']
                here = ndb.GeoPt(float(lat), float(lon))
            except:
                here = self.user_prefs.locpt
            # try:
            dist = 100
            now = datetime.now().strftime('%Y-%m-%d')
            later = (datetime.now() + timedelta(365)).strftime('%Y-%m-%d')
            results = search_points_start(dist,'REQUEST_INDEX',later,now,'delivby','start',here)
            rdump = {'status':'ok'}
            logging.info(results)
            rdump['count'] = len(results.results)
            rdump['link'] = '/search/reqhome?startlat='+str(here.lat)+'&startlon='+str(here.lon)
            # except:
                # rdump = {'status':'fail'}
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(rdump))
        elif action=='dumpreqsdest':
            data = json.loads(self.request.body)
            self.response.headers['Content-Type'] = "application/json"
            # try:
            posts = []
            key = data.get('key')
            if key:
                r = ndb.Key(urlsafe=key).get()
            else:
                return
            rdump = {'status':'ok'}
            path = data.get('legs')
            pathpts = data.get('legs')
            precision = data.get('precision')
            if not pathpts or not precision:
                return
            results = search_requests(r.start,r.dest,None,pathpts,None,None,precision)
            for r in results:
                posts.append(r)
            rdump['posts'] = posts
            rdump['count'] = len(posts)
            # except:
                # rdump = {'status': 'fail'}
            self.write(json.dumps(rdump))
        elif action=='dumproutesdest':
            data = json.loads(self.request.body)
            self.response.headers['Content-Type'] = "application/json"
            # try:
            posts = []
            key = data['key']
            r = ndb.Key(urlsafe=key).get()
            rdump = {'status':'ok'}
            later = (datetime.now() + timedelta(365))
            req = Request(start=r.start, dest=r.dest, delivby=later)
            results = find_routematch(req)
            for r in results:
                posts.append(r.get().to_search())
            rdump['posts'] = posts
            rdump['count'] = len(posts)
            # except:
                # rdump = {'status': 'fail'}
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
            unroll=unroll + "\n" + p['start'] + "\t" + p['dest'] + "\t" + p['delivby'] + "\t" + www_home + p['post_url']
        params = {'posts': posts}
        unrollparams = {'posts': unroll}
        self.params['action'] = 'match2driver'
        self.params['senderid'] = 'barnacle'
        self.params['receiverid'] = driver.id()
        self.send_match2d(driver.get().email, params, unrollparams)

    def __send_match2s(self,sender):
        reqs = Request.by_userkey(sender)
        matches = []
        for r in reqs:
            matches = matches + r.matches
        posts = []
        unroll=""
        for m in matches:
            # check if it's a RT
            p = m.get().to_search()
            if p['thumb_url'][0]=='/':
                p['thumb_url'] = www_home + p['thumb_url']
            posts.append(p)
            unroll=unroll + "\n" + p['start'] + "\t" + p['dest'] + "\t"
            if p['roundtrip'] == 1:
                unroll = unroll + "Roundtrip"
            unroll = unroll + "\t" + p['delivend'] + "\t" + www_home + p['post_url']
        params = {'posts': posts}
        unrollparams = {'posts': unroll}
        self.params['action'] = 'match2sender'
        self.params['senderid'] = 'barnacle'
        self.params['receiverid'] = sender.id()
        self.send_match2s(sender.get().email, params, unrollparams)

    def send_match2d(self, email, params, unrollparams):
        """Send match to driver"""
        htmlbody =  self.render_str('email/requestnote.html', **params)
        textbody = requestnote_txt % unrollparams
        send_info(to_email=email, subject=request_note_sub,
            body=textbody, html=htmlbody)

    def send_match2s(self, email, params, unrollparams):
        """Send match to sender"""
        htmlbody =  self.render_str('email/routenote.html', **params)
        textbody = routenote_txt % unrollparams
        send_info(to_email=email, subject=request_note_sub,
            body=textbody, html=htmlbody)

    def __updatereq(self,r):
        r.matches =  find_routematch(r)
        r.put()
    def __updateroute(self,r):
        r.matches =  find_reqmatch(r)
        r.put()

def find_reqmatch(route):
    # for a given route, get all matching requests
    # Use stored pathpts, generate Haversin Dist
    dist = HaversinDist(route.start.lat, route.start.lon, route.dest.lat, route.dest.lon)
    # increase fudge because we only stored [0::100]
    precision = precisionDist(dist)-3
    pathpts = [roundPoint(pp, precision) for pp in route.pathpts]
    results = Request.search_route(pathpts, route.delivstart, route.delivend, precision)
    if route.roundtrip:
        results = results + Request.search_route(list(reversed(pathpts)), route.delivend, route.delivend, precision)
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
