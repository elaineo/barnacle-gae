from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from google.appengine.api import memcache
from Handlers.Post.Post import PostHandler
from Models.Post.Route import *

from Models.User.Driver import *

from Utils.RouteUtils import RouteUtils
from Utils.SearchDocUtils import create_route_doc
from Utils.ValidUtils import *
from Utils.data.routesub import ROUTE_I5

import logging
import json
import time

class RouteHandler(PostHandler):
    """ Post a new route """
    def get(self, action=None,key=None):
        if not action and key: 
            self.view_page(key)
        if not action and self.user_prefs:
            self.params['createorupdate'] = 'Ready to Drive'
            d = Driver.by_userkey(self.user_prefs.key)
            if not d: #not an existing driver
                self.params.update(self.user_prefs.params_fill())
                self.render('user/forms/filldriver.html', **self.params)
                return
            self.params['location'] = self.user_prefs.location
            self.params['route_title'] = 'Drive a New Route'
            self.params['substart'] = 'Seattle, WA'
            self.params['subdest'] = 'San Diego, CA'
            self.params['route_action'] = '/route'
            self.render('post/forms/fillpost.html', **self.params)    
        if action=='json' and not key:
            # dump route map
            self.response.headers['Content-Type'] = "application/json"
            jsonall_result = memcache.get('jsonall')
            if jsonall_result is not None:
                self.write(jsonall_result)
                return
            else:
                routes = Route.query(Route.dead==0)
                rdump = RouteUtils.dumpall(routes)
                jsonall_result = special_json_format(rdump)
                memcache.add(key="jsonall", value=jsonall_result, time=3600)
                self.write(jsonall_result)
                return
        elif action=='json':
            # dump single route map
            try:
                route=ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            rdump = RouteUtils.dumproute(route)
            self.response.headers['Content-Type'] = "application/json"
            self.write(rdump)
        elif action=='edit' and key:
            try:
                p = ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            if not self.user_prefs:
                self.redirect('/#signin-box')
                return
            if p.key.parent() == self.user_prefs.key:
                self.params.update(p.to_dict(True))
                self.params['route_title'] = 'Edit Route'
                self.params['route_action'] = '/route/'+key
                self.render('post/forms/fillpost.html', **self.params)
                return
            logging.error(p)
            self.abort(403)
            return


    def post(self, action=None,key=None):
        if not self.user_prefs:
            self.redirect('/#signin-box')      
        if action=='subscribe':
            self.__subscribe()
            return
        if action=='edit' and key:
            try:
                p = ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            if p.key.parent() == self.user_prefs.key:
                self.__create_route(key)
            logging.error(p)
            self.abort(403)
            return
        elif action=='delete' and key:
            self.delete(key)            
        else:
            self.__create_route(key)

        
    def __subscribe(self):
        self.response.headers['Content-Type'] = "application/json"        
        data = json.loads(unicode(self.request.body, errors='replace'))    
        response = {'status':'ok'}
        start, startstr = get_search_json(data,'substart')
        dest, deststr = get_search_json(data,'subdest')    
        capacity = data.get('vcap')
        capacity = parse_unit(capacity)
        details = data.get('details')        
        subroute = parse_unit(data.get('hidesub'))
        # see if this user has any existing subs
        subs = Route.by_subscriber(self.user_prefs.key)
        if subroute in subs:
            new_r = False
            s = subs.filter(Route.subscribe==subroute).get()
        else:
            new_r = True
            delivstart = datetime.now()
            delivend = datetime.now()+timedelta(days=365)
            s = Route(parent=self.user_prefs.key, stats=RouteStats(),
                delivstart=delivstart, delivend=delivend, roundtrip=True)
        s.locstart=startstr
        s.locend=deststr
        s.start=start
        s.dest=dest
        s.capacity=capacity
        s.details=details
        s.pathpts = RouteUtils.pathSub(start,dest,ROUTE_I5)
        s.put()
        logging.info('New Route Subscription: '+startstr+' to '+deststr)
        taskqueue.add(url='/match/updateroute/'+s.key.urlsafe(), method='get')
        create_route_doc(s.key.urlsafe(), s, new_r)
        if new_r:
            taskqueue.add(url='/notify/thanks/'+s.key.urlsafe(), method='get')
        add_roundtrip(s, new_r)
        response['next'] = '/account'
        self.write(json.dumps(response))
    
    def __create_route(self,key=None):
        self.response.headers['Content-Type'] = "application/json"        
        response = {'status':'ok'}
        data = json.loads(unicode(self.request.body, errors='replace'))
        capacity = data.get('vcap')
        rtr = data.get('rtr')
        rtr = parse_bool(rtr)
        capacity = parse_unit(capacity)

        details = data.get('details')
        startdate = data.get('delivstart')
        enddate = data.get('delivend')
        if startdate:
            delivstart = parse_date(startdate)
        else:
            delivstart = datetime.now()
        if enddate:
            delivend = parse_date(enddate)
        else:
            delivend = datetime.now()+timedelta(days=30)

        start, startstr = get_search_json(data,'start')
        dest, deststr = get_search_json(data,'dest')

        if key: # if editing post
            new_r = False
            p = ndb.Key(urlsafe=key).get()
            if p and self.user_prefs and p.key.parent() == self.user_prefs.key:
                p.details = details
                p.capacity = capacity
                p.delivstart = delivstart
                p.delivend = delivend
                p.locstart = startstr
                p.locend = deststr
                p.dest = dest
                p.start = start
                if not p.roundtrip and rtr: #added a return trip
                    add_roundtrip(p, True)
                if p.roundtrip and not rtr: #deleted return trip
                    delete_doc(p.key.urlsafe()+'_RT',p.__class__.__name__)
                p.roundtrip = rtr
            else:
                response = {'status':'fail'}
                self.write(json.dumps(response))
                return
        else: # new post
            new_r = True
            p = Route(parent=self.user_prefs.key, stats=RouteStats(),
                locstart=startstr, locend=deststr,
                start=start, dest=dest, capacity=capacity, details=details,
                delivstart=delivstart, delivend=delivend, roundtrip=rtr)
            logging.info('New Route: '+startstr+' to '+deststr)

        path = data.get('legs')
        distance = data.get('distance')
        p.pathpts = [ndb.GeoPt(lat=q[0],lon=q[1]) for q in path]
        p.pathpts.insert(0,start)
        p.pathpts.append(dest)

        p.put()
        taskqueue.add(url='/match/updateroute/'+p.key.urlsafe(), method='get')
        create_route_doc(p.key.urlsafe(), p, new_r)
        if new_r:
            taskqueue.add(url='/notify/thanks/'+p.key.urlsafe(), method='get')
        if rtr:
            add_roundtrip(p, new_r)
        fbshare = data.get('fbshare')
        fbshare = parse_bool(fbshare)
        share_onload=''
        if fbshare and new_r:
            share_onload='?fb'        
        response['next'] = '/route/'+p.key.urlsafe()+share_onload
        self.write(json.dumps(response))


def add_roundtrip(route, new_r):
    p2 = Route(parent=route.key.parent(),
            locstart=route.locend, locend=route.locstart,
            start=route.dest, dest=route.start,
            capacity=route.capacity, details=route.details,
            delivstart=route.delivend, delivend=route.delivend,
            roundtrip=route.roundtrip,repeatr=route.repeatr,
            pathpts=route.pathpts)
    create_route_doc(route.key.urlsafe()+'_RT', p2, new_r)


    
def special_json_format(rdump):
    rdump['paths'] = [[('%1.2f' % a, '%1.2f' % b) for a, b in pathpts] for pathpts in rdump['paths']]
    jsonall_result = json.dumps(rdump, separators=(',',':'))
    jsonall_result = jsonall_result.replace('"','').replace('paths','"paths"').replace('zoom','"zoom"').replace('center','"center"')
    return jsonall_result    
