from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from Handlers.BaseHandler import *
from Models.RouteModel import *
from Models.RequestModel import *
from Models.Launch.Driver import *
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
            routes = Route.get_all()
            rdump = RouteUtils().dumpall(routes)
            self.write(json.dumps(rdump))
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
            if p.userkey == self.user_prefs.key:
                if p.__class__.__name__ == 'Route':
                    self.params.update(fill_route_params(key,True))
                    self.params['route_title'] = 'Edit Route'
                    self.render('forms/fillpost.html', **self.params)
                else:
                    self.params.update(fill_route_params(key,False))
                    self.params['route_title'] = 'Edit Delivery Request'
                    self.render('forms/editrequest.html', **self.params)      
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
                self.params.update(savsearch.params_fill(self.params))
            self.params['route_title'] = 'Post a Delivery Request'
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('forms/fillrequest.html', **self.params)
        elif key: # check if user logged in
            self.view_page(key)
        elif self.user_prefs:
            self.params['createorupdate'] = 'Ready to Drive'
            d = Driver.by_userkey(self.user_prefs.key)
            if not d: #not an existing driver
                self.params.update(self.user_prefs.params_fill(self.params))
                self.render('forms/filldriver.html', **self.params)
                return
            self.params['route_title'] = 'Drive a New Route'
            self.render('forms/fillpost.html', **self.params)
        else:
            self.redirect('/#signin-box') 
            
    def post(self, action=None,key=None):
        if action=='request':
            self.__create_request(key)
        elif action=='request0':
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
            if p.userkey == self.user_prefs.key:
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
        if key:
            r = ndb.Key(urlsafe=key).get()
            if r and r.userkey==self.user_prefs.key:
                # check to make sure nothing was confirmed
                # delete associated reservations                
                type = r.__class__.__name__
                if type=='Route':
                    if Reservation.route_confirmed(r.key)>0:
                        return
                    res = Reservation.by_route(r.key)
                    for q in res:
                       q.key.delete() 
                    if r.roundtrip:
                        delete_doc(r.key.urlsafe()+'_RT',type) 
                elif type=='Request':
                    if DeliveryOffer.route_confirmed(r.key)>0:
                        return
                    res = DeliveryOffer.by_route(r.key)
                    for q in res:
                       q.key.delete()           
                # delete from matches
                taskqueue.add(url='/match/cleanmatch/'+key, method='get')
                # delete in search docs
                delete_doc(r.key.urlsafe(),type)
                r.key.delete()
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
        if p and self.user_prefs and p.userkey == self.user_prefs.key:  
            p.rates = rates
            p.items = items
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
            self.params['items'] = items
            self.params['capacity'] = capacity
            self.params['delivby'] = reqdate
            self.params['rates'] = rates
            self.params['route_title'] = 'Edit Delivery Request'
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('forms/fillrequest.html', **self.params)
    def __init_request(self,key=None):
        self.response.headers['Content-Type'] = "application/json"        
        response = {'status':'ok'}
        data = json.loads(unicode(self.request.body, errors='replace'))
        capacity = data.get('vcap')
        capacity = parse_unit(capacity)    
        #items = self.request.get('items')
        reqdate = data.get('reqdate')     
        if reqdate:
            delivby = parse_date(reqdate)
        else:
            delivby = datetime.now()+timedelta(weeks=1)
        
        start, startstr = get_search_json(data,'start')
        dest, deststr = get_search_json(data,'dest')  
        
        logging.info('Initial Request: '+startstr+' to '+deststr)
        distance = data.get('distance')
        p = Request(userkey=self.user_prefs.key, start=start, 
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
            self.render('request_review.html', **self.params)            
            taskqueue.add(url='/match/updatereq/'+p.key.urlsafe(), method='get')
            taskqueue.add(url='/summary/selfnote/'+p.key.urlsafe(), method='get')
            create_request_doc(p.key.urlsafe(), p)            

        except:  #this should never happen
            self.params['error_route'] = 'Invalid Locations'
            self.params['capacity'] = capacity
            self.params['delivby'] = reqdate
            self.params['route_title'] = 'Edit Delivery Request'
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('forms/fillrequest.html', **self.params)  
            
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
        if p and self.user_prefs and p.userkey == self.user_prefs.key:  
            if img: 
                imgstore = ImageStore.new(img)
                imgstore.put()
                p.img_id = imgstore.key.id()
            p.rates = rates
            p.items = items
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
            if len(weekr)==0:
                repeatr=2
            else:
                dayweek = [int(w) for w in weekr]
                rr = RepeatRoute(period=repeatr, dayweek=dayweek,weekmonth=[])
        if (repeatr==1):
            monthr = data.get('monthr')
            if len(monthr)==0:
                repeatr=0
            else:
                rr.weekmonth = [int(m) for m in monthr]
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
            if p and self.user_prefs and p.userkey == self.user_prefs.key:  
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
            p = Route(userkey=self.user_prefs.key, stats=RouteStats(),
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
            p.increment_views()
            if self.user_prefs and self.user_prefs.key == p.userkey:
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
                self.render('post.html', **self.params)
            else:
                self.params.update(fill_route_params(key,False))
                self.render('request.html', **self.params)
            return
        else:        
            #see if it's expired
            expr = get_expired(key)
            if expr: # display expired pages
                self.params.update(expr.to_dict())
                if expr.__class__.__name__ == 'ExpiredRoute':                
                    self.render('landing/exppost.html', **self.params)
                else:
                    self.render('landing/exprequest.html', **self.params)
            else:
                self.abort(409)
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

def get_expired(key):
    p = ExpiredRequest.by_key(ndb.Key(urlsafe=key))
    if not p:
        p = ExpiredRoute.by_key(ndb.Key(urlsafe=key))
    return p
        
def add_roundtrip(route):
    p2 = Route(userkey=route.userkey, locstart=route.locend, locend=route.locstart, 
                start=route.dest, dest=route.start, 
                capacity=route.capacity, details=route.details, 
                delivstart=route.delivend, delivend=route.delivend, 
                roundtrip=route.roundtrip,repeatr=route.repeatr,
                pathpts=route.pathpts)
    create_route_doc(route.key.urlsafe()+'_RT', p2)

        
def fill_route_params(key,is_route=False):
    p = ndb.Key(urlsafe=key).get()
    u = p.userkey.get()
    params = {
        'reserve_url' : p.reserve_url(),
        'edit_url' : p.edit_url(),
        'delete_url':p.delete_url(),        
        'routekey' : key,
        'locstart' : p.locstart,
        'locend' : p.locend,
        'capacity' : p.capacity,
        'num_confirmed' : p.num_confirmed(),
        'num_matches' : len(p.matches),
        'msg_ok' : True #(0 in u.get_notify())
        }
    params.update(u.params_fill_sm(params))
    d = Driver.by_userkey(p.userkey)
    if d:
        params.update(d.params_fill(params))
    #else: they must be a driver if they have a route...
    if is_route:
        params.update({ 'details' : p.details,
                        'num_requests' : p.num_requests(),
                        'sugg_rate' :p.suggest_rate(),
                        'rt' : int(p.roundtrip),
                        'delivstart' : p.delivstart.strftime('%m/%d/%Y'),
                        'delivend' : p.delivend.strftime('%m/%d/%Y') })
        params.update(p.gen_repeat())
    else:
        params.update({ 'items' : p.items,
                        'img_url' : p.image_url(),
                        'img_thumb' : p.image_url('small'),
                        'num_offers' : p.num_offers(),
                        'rates' : p.rates,
                        'delivby' : p.delivby.strftime('%m/%d/%Y') })    
    message_url = '/message?'
    message_url += 'receiver=' + u.key.urlsafe() + '&subject=' +p.locstart+' to ' +p.locend
    params['message_url'] = message_url
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
            for q in Reservation.by_route(r.key):
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
            for q in DeliveryOffer.by_route(r.key):
                offdump.append(q.to_dict())
            dump['offers'] = offdump
            reqdump.append(dump)        
        return reqdump
    def __resdump(self, key):
        resdump = []
        for q in Reservation.by_sender(key):
            resdump.append(q.to_dict())            
        # Also dump fixed-route things
        return resdump
    def __offdump(self, key):
        offdump = []
        for q in DeliveryOffer.by_sender(key):
            offdump.append(q.to_dict())
        return offdump        
    def __compdump(self, key):
        compdump = []
        for q in ExpiredOffer.by_sender(key):
            compdump.append(q.to_dict())
        for q in ExpiredOffer.by_receiver(key):
            compdump.append(q.to_dict())            
        for q in ExpiredReservation.by_receiver(key):
            compdump.append(q.to_dict())                  
        for q in ExpiredReservation.by_sender(key):
            compdump.append(q.to_dict())                              
        return compdump         

        
def route_resdump(key, name):
    resdump = []
    if name=='Route':
        for q in Reservation.by_route(key):
            resdump.append(q.to_dict())
    elif name=='Request':
        for q in DeliveryOffer.by_route(key):
            resdump.append(q.to_dict())           
    return resdump                
    
def route_matchdump(route):
    resdump = []
    for q in route.matches:
        k = q.get()
        if k:
            resdump.append(k.to_dict())
    return resdump      