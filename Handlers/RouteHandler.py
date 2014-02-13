from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from google.appengine.api import memcache
from Handlers.BaseHandler import *
from Models.Post.Route import *
from Models.Post.Request import *
from Models.Post.OfferRoute import *
from Models.Post.OfferRequest import *
from Models.User.Driver import *
from Utils.RouteUtils import *
from Utils.SearchDocUtils import create_route_doc
from Utils.SearchDocUtils import create_request_doc
from Utils.SearchDocUtils import delete_doc
from Utils.ValidUtils import *
import logging
import json
import time

class RouteHandler(BaseHandler):
    """ Post a new route """
    def get(self, action=None,key=None):
        if action=='jsonall':
            self.response.headers['Content-Type'] = "application/json"
            jsonall_result = memcache.get('jsonall')
            if jsonall_result is not None:
                self.write(jsonall_result)
                return
            else:
                routes = Route.query()
                rdump = RouteUtils().dumpall(routes)
                jsonall_result = json.dumps(rdump)
                memcache.add(key="jsonall", value=jsonall_result, time=3600)
                self.write(jsonall_result)
                return
        elif action=='jsonroute' and key:
            try:
                route=ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            if route.__class__.__name__ =='Route':
                rdump = RouteUtils().dumproute(route)
            else:
                rdump = RouteUtils().dumppts([route.start,route.dest])
            self.response.headers['Content-Type'] = "application/json"
            self.write(rdump)
        elif action=='edit' and key:
            try:
                p = ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            if not self.user_prefs:
                self.redirect('/post#signin-box')
                return
            if p.key.parent() == self.user_prefs.key:
                if p.__class__.__name__ == 'Route':
                    self.params.update(fill_route_params(key,True))
                    self.params['route_title'] = 'Edit Route'
                    self.render('post/forms/fillpost.html', **self.params)
                else:
                    self.params.update(fill_route_params(key,False))
                    self.params['route_title'] = 'Edit Delivery Request'
                    self.render('post/forms/editrequest.html', **self.params)
                return
            logging.error(p)
            self.abort(403)
            return
        elif action=='request' and not key:
            remoteip = self.request.remote_addr
            savsearch = SearchEntry.by_ip(remoteip)
            pop = self.request.get('pop')
            # create new request post
            if savsearch and bool(pop):
                self.params.update(savsearch.params_fill())
            self.params['route_title'] = 'Post a Delivery Request'
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('post/forms/fillrequest.html', **self.params)
        elif key: # check if user logged in
            self.view_page(key)
        elif self.user_prefs:
            self.params['createorupdate'] = 'Ready to Drive'
            d = Driver.by_userkey(self.user_prefs.key)
            if not d: #not an existing driver
                self.params.update(self.user_prefs.params_fill())
                self.render('user/forms/filldriver.html', **self.params)
                return
            self.params['route_title'] = 'Drive a New Route'
            self.render('post/forms/fillpost.html', **self.params)
        else:
            self.redirect('/#signin-box')

    def post(self, action=None,key=None):
        if action=='request0':
            self.__init_request()
        elif action=='update' and key:
            self.__update_request(key)
        elif action=='edit' and key:
            try:
                p = ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return

            if not self.user_prefs:
                self.redirect('/post#signin-box')
                return
            if p.key.parent() == self.user_prefs.key:
                if p.__class__.__name__ == 'Route':
                    self.__create_route(key)
                else:
                    self.__create_request(key)
                return
            logging.error(p)
            self.abort(403)
            return
        elif action=='delete' and key:
            self.__delete(key)
        else:
            self.__create_route(key)

    def __delete(self, key=None):
        if key and self.user_prefs:
            r = ndb.Key(urlsafe=key).get()
            if r and r.key.parent()==self.user_prefs.key:
                # check to make sure nothing was confirmed
                # delete associated reservations
                type = r.__class__.__name__
                if r.num_confirmed() > 0:
                    return
                for q in r.offers:
                    q.get().dead = PostStatus.index('DELETED')
                    q.put()
                if type=='Route':
                    if r.roundtrip:
                        delete_doc(r.key.urlsafe()+'_RT',type)
                # delete from matches
                taskqueue.add(url='/match/cleanmatch/'+key, method='get')
                # delete in search docs
                delete_doc(r.key.urlsafe(),type)
                r.dead = PostStatus.index('DELETED')
                r.put()
                self.redirect('/account')
            else:
                self.abort(403)
                return

    def __create_request(self,key=None):
        capacity = self.request.get('vcap')
        capacity = parse_unit(capacity)
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        items = self.request.get('items')
        reqdate = self.request.get('reqdate')
        img = self.request.get("file")
        if reqdate:
            delivby = parse_date(reqdate)
        else:
            delivby = datetime.now()+timedelta(weeks=1)

        start, startstr = self.__get_map_form('start')
        dest, deststr = self.__get_map_form('dest')
        logging.info('New Request: '+startstr+' to '+deststr)

        p = ndb.Key(urlsafe=key).get()
        if p and self.user_prefs and p.key.parent() == self.user_prefs.key:
            p.rates = rates
            p.details = items
            p.delivby = delivby
            p.locstart = startstr
            p.locend = deststr
            p.start = start
            p.dest = dest
            p.capacity=capacity
            if img:
                if p.img_id: # existing image
                    imgstore = ImageStore.get_by_id(p.img_id)
                    imgstore.update(img)
                else: # new image
                    imgstore = ImageStore.new(img)
                imgstore.put()
                p.img_id = imgstore.key.id()
        else:
            self.redirect('/post/request')
        try:
            p.put()
            taskqueue.add(url='/match/updatereq/'+p.key.urlsafe(), method='get')
            taskqueue.add(url='/summary/selfnote/'+p.key.urlsafe(), method='get')
            create_request_doc(p.key.urlsafe(), p)
            fbshare = bool(self.request.get('fbshare'))
            self.params['share_onload'] = fbshare
            self.view_page(p.key.urlsafe())
        except:
            self.params['error_route'] = 'Invalid Locations'
            self.params['details'] = items
            self.params['capacity'] = capacity
            self.params['delivby'] = reqdate
            self.params['rates'] = rates
            self.params['route_title'] = 'Edit Delivery Request'
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('post/forms/fillrequest.html', **self.params)
            
    def __init_request(self,key=None):
        self.response.headers['Content-Type'] = "application/json"
        response = {'status':'ok'}
        data = json.loads(unicode(self.request.body, errors='replace'))
        capacity = data.get('vcap')
        capacity = parse_unit(capacity)
        reqdate = data.get('reqdate')
        if reqdate:
            delivby = parse_date(reqdate)
        else:
            delivby = datetime.now()+timedelta(weeks=1)

        start, startstr = get_search_json(data,'start')
        dest, deststr = get_search_json(data,'dest')

        logging.info('Initial Request: '+startstr+' to '+deststr)
        distance = data.get('distance')
        p = Request(parent=self.user_prefs.key, start=start,
            dest=dest, capacity=capacity,
            delivby=delivby, locstart=startstr, locend=deststr)

        price, seed = priceEst(p, distance)
        stats = ReqStats(sugg_price = price, seed = seed, distance = distance)
        p.rates = 0
        p.stats = stats

        try:
            p.put()
            self.params.update(fill_route_params(p.key.urlsafe(),False))
            self.params['update_url'] = '/post/update/' + p.key.urlsafe()
            self.params['email'] = self.user_prefs.email
            self.params['rates'] = price
            self.render('post/request_review.html', **self.params)
            taskqueue.add(url='/match/updatereq/'+p.key.urlsafe(), method='get')
            create_request_doc(p.key.urlsafe(), p)

        except:  #this should never happen
            self.params['error_route'] = 'Invalid Locations'
            self.params['capacity'] = capacity
            self.params['delivby'] = reqdate
            self.params['route_title'] = 'Edit Delivery Request'
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('post/forms/fillrequest.html', **self.params)

    def __update_request(self,key):
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        items = self.request.get('items')
        email = self.request.get('email')
        if email and (email != self.user_prefs.email):
            u = self.user_prefs.key.get()
            u.email = email
            u.put()
        p = ndb.Key(urlsafe=key).get()
        # image upload
        img = self.request.get("file")
        if p and self.user_prefs and p.key.parent() == self.user_prefs.key:
            if img:
                imgstore = ImageStore.new(img)
                imgstore.put()
                p.img_id = imgstore.key.id()
            p.rates = rates
            p.details = items
            # get a cc #
            p.stats.status = RequestStatus.index('PURSUE')
            p.put()
            self.view_page(p.key.urlsafe())
        else:
            self.redirect('/post/request')

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
        try:
            p.pathpts = pathPrec(start, path, distance)
        except:
            #Somehow, the front end did not return this data. must be invalid route
            # p.pathpts, dist = getPath(start,dest)
            response = {'status':'invalid'}
            self.write(json.dumps(response))
            return
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
        response['next'] = '/post/'+p.key.urlsafe()+share_onload
        self.write(json.dumps(response))

    def view_page(self,keyrt):
        if keyrt.endswith('_RT'):
            key = keyrt[:-3]
        else:
            key = keyrt
        p = ndb.Key(urlsafe=key).get()
        if p:
            if p.dead > 0:
                view_dead(p)
                return
            p.increment_views()
            if self.user_prefs and self.user_prefs.key == p.key.parent():
                self.params['edit_allow'] = True
                if p.num_confirmed > 0:
                    self.params['resdump'] = route_resdump(p.key, p.__class__.__name__)
                if len(p.matches) > 0:
                    self.params['matchdump'] = route_matchdump(p)
            else:
                self.params['edit_allow'] = False
            if self.user_prefs and self.user_prefs.account_type == 'fb':
                self.params['fb_share'] = True
            if p.__class__.__name__ == 'Route':
                self.params.update(fill_route_params(key,True))
                self.render('post/post.html', **self.params)
            else:
                self.params.update(fill_route_params(key,False))
                self.render('post/request.html', **self.params)
        else:
            self.abort(409)
        return

    def view_dead(route):
        self.params.update(route.to_dict())
        if route.__class__.__name__ == 'Route':
            self.render('landing/exppost.html', **self.params)
        else:
            self.render('landing/exprequest.html', **self.params)
        return
        
    def __get_map_form(self,pt):
        ptlat = self.request.get(pt+'lat')
        ptlon = self.request.get(pt+'lon')
        ptstr = self.request.get(pt+'str')
        if not ptstr or not ptlat or not ptlon:
            ptstr = self.request.get(pt)
            if ptstr:
                ptg = RouteUtils().getGeoLoc(ptstr)[0]
            else:
                ptg = None
        else:
            ptg = ndb.GeoPt(lat=ptlat,lon=ptlon)
        return ptg, ptstr


def add_roundtrip(route):
    p2 = Route(parent=route.key.parent(), 
                locstart=route.locend, locend=route.locstart,
                start=route.dest, dest=route.start,
                capacity=route.capacity, details=route.details,
                delivstart=route.delivend, delivend=route.delivend,
                roundtrip=route.roundtrip,repeatr=route.repeatr,
                pathpts=route.pathpts)
    create_route_doc(route.key.urlsafe()+'_RT', p2)


def fill_route_params(key,is_route=False):
    p = ndb.Key(urlsafe=key).get()
    u = p.key.parent().get()
    params = p.to_dict()
    params.update(u.params_fill_sm())
    d = Driver.by_userkey(u.key)
    if d:
        params.update(d.params_fill())
    params['userkey'] = u.key.urlsafe()
    return params

class DumpHandler(BaseHandler):
    def get(self, key=None):
        if not self.user_prefs.key:
            self.abort(403)
            return
        routedump = self.__routedump(self.user_prefs.key)
        reqdump = self.__reqdump(self.user_prefs.key)
        resdump = self.__resdump(self.user_prefs.key)
        offdump = self.__offdump(self.user_prefs.key)
        compdump = self.__compdump(self.user_prefs.key)
        if routedump:
            self.params['disproute'] = True
        else:
            self.params['disproute'] = False
        if reqdump:
            self.params['dispreq'] = True
        else:
            self.params['dispreq'] = False
        if resdump:
            self.params['dispres'] = True
        else:
            self.params['dispres'] = False
        if offdump:
            self.params['dispoff'] = True
        else:
            self.params['dispoff'] = False
        if compdump:
            self.params['dispcomp'] = True
        else:
            self.params['dispcomp'] = False
        self.params['routedump'] = routedump
        self.params['reqdump'] = reqdump
        self.params['resdump'] = resdump
        self.params['offdump'] = offdump
        self.params['compdump'] = compdump
        self.render('routes_reqs.html', **self.params)

    def __routedump(self, key):
        routedump = []
        routes = Route.by_userkey(key)
        for r in routes:
            dump = r.to_dict()
            resdump = []
            for q in OfferRequest.by_route(r.key):
                resdump.append(q.to_dict())
            dump['reservations'] = resdump
            routedump.append(dump)
        return routedump
    def __reqdump(self, key):
        reqdump = []
        requests = Request.by_userkey(key)
        for r in requests:
            dump = r.to_dict()
            offdump = []
            for q in OfferRoute.by_route(r.key):
                offdump.append(q.to_dict())
            dump['offers'] = offdump
            reqdump.append(dump)
        return reqdump
    def __resdump(self, key):
        resdump = []
        for q in OfferRequest.by_user(key):
            resdump.append(q.to_dict())
        # Also dump fixed-route things
        return resdump
    def __offdump(self, key):
        offdump = []
        for q in OfferRoute.by_user(key):
            offdump.append(q.to_dict())
        return offdump
    def __compdump(self, key):
        compdump = []
        for q in OfferRoute.by_user(key,1):
            compdump.append(q.to_dict())
        for q in OfferRequest.by_user(key,1):
            compdump.append(q.to_dict())
        return compdump


def route_resdump(key, name):
    resdump = []
    if name=='Route':
        for q in OfferRequest.by_route(key):
            resdump.append(q.to_dict())
    elif name=='Request':
        for q in OfferRoute.by_route(key):
            resdump.append(q.to_dict())
    return resdump

def route_matchdump(route):
    resdump = []
    for q in route.matches:
        k = q.get()
        if k:
            resdump.append(k.to_dict())
    return resdump
