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
            self.params['route_title'] = 'Drive a New Route'
            self.render('post/forms/fillpost.html', **self.params)    
        if action=='json' and not key:
            # dump route map
            self.response.headers['Content-Type'] = "application/json"
            jsonall_result = memcache.get('jsonall')
            if jsonall_result is not None:
                self.write(jsonall_result)
                return
            else:
                routes = Route.query()
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
                self.render('post/forms/fillpost.html', **self.params)
                return
            logging.error(p)
            self.abort(403)
            return


    def post(self, action=None,key=None):
        if not self.user_prefs:
            self.redirect('/#signin-box')            
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


    def __create_route(self,key=None):
        self.response.headers['Content-Type'] = "application/json"
        response = {'status':'ok'}
        data = json.loads(unicode(self.request.body, errors='replace'))
        capacity = data.get('vcap')
        repeatr = int(data.get('repeatr'))
        rtr = bool(data.get('rtr'))
        capacity = parse_unit(capacity)
        if (repeatr<2):
            weekr = data.get('weekr')
            try:
                dayweek = [int(w) for w in weekr]
                rr = RepeatRoute(period=repeatr, dayweek=dayweek,weekmonth=[])
            except:
                repeatr=2
        if (repeatr==1):
            monthr = data.get('monthr')
            try:
                rr.weekmonth = [int(m) for m in monthr]
            except:
                repeatr=0
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
            delivend = datetime.now()+timedelta(weeks=1)

        start, startstr = get_search_json(data,'start')
        dest, deststr = get_search_json(data,'dest')
        logging.info('New Route: '+startstr+' to '+deststr)

        if key: # if editing post
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
                    add_roundtrip(p)
                if p.roundtrip and not rtr: #deleted return trip
                    delete_doc(p.key.urlsafe()+'_RT',p.__class__.__name__)
                p.roundtrip = rtr
            else:
                response = {'status':'fail'}
                self.write(json.dumps(response))
                return
        else: # new post
            p = Route(parent=self.user_prefs.key, stats=RouteStats(),
                locstart=startstr, locend=deststr,
                start=start, dest=dest, capacity=capacity, details=details,
                delivstart=delivstart, delivend=delivend, roundtrip=rtr)
        if (repeatr<2):
            p.repeatr = rr
        else:
            p.repeatr = None
        path = data.get('legs')
        distance = data.get('distance')
        p.pathpts = [ndb.GeoPt(lat=q[0],lon=q[1]) for q in path]
        p.pathpts.insert(0,start)
        p.pathpts.append(dest)
        # try:
            # p.pathpts = RouteUtils.pathPrec(start, path, distance)
        # except:
            # response = {'status':'invalid'}
            # self.write(json.dumps(response))
            # return
        p.put()
        taskqueue.add(url='/match/updateroute/'+p.key.urlsafe(), method='get')
        create_route_doc(p.key.urlsafe(), p)
        if rtr:
            add_roundtrip(p)
        fbshare = bool(data.get('fbshare'))
        #self.params['share_onload'] = fbshare
        share_onload=''
        if fbshare:
            share_onload='?fb'
        response['next'] = '/route/'+p.key.urlsafe()+share_onload
        self.write(json.dumps(response))


def add_roundtrip(route):
    p2 = Route(parent=route.key.parent(),
                locstart=route.locend, locend=route.locstart,
                start=route.dest, dest=route.start,
                capacity=route.capacity, details=route.details,
                delivstart=route.delivend, delivend=route.delivend,
                roundtrip=route.roundtrip,repeatr=route.repeatr,
                pathpts=route.pathpts)
    create_route_doc(route.key.urlsafe()+'_RT', p2)


    
def special_json_format(rdump):
    rdump['paths'] = [[('%1.2f' % a, '%1.2f' % b) for a, b in pathpts] for pathpts in rdump['paths']]
    jsonall_result = json.dumps(rdump, separators=(',',':'))
    jsonall_result = jsonall_result.replace('"','').replace('paths','"paths"').replace('zoom','"zoom"').replace('center','"center"')
    return jsonall_result    
