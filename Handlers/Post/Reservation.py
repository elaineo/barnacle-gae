from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from Handlers.BaseHandler import *
from Handlers.Launch.CheckoutHandler import *
from Handlers.Tracker.TrackerHandler import create_from_res
from Handlers.MessageHandler import create_message
from Models.Post.OfferRequest import *
from Models.Post.OfferRoute import *
from Models.Post.Request import *
from Models.Post.Route import *
from Models.User.Driver import *
from Utils.RouteUtils import RouteUtils
from Utils.ValidUtils import *
from Utils.EmailUtils import create_note
from Utils.Email.Reservation import *
import logging

class ReservationHandler(BaseHandler):
    """ Make a Reservation """
    def get(self, action=None,key=None):
        if action=='edit':
            if not self.user_prefs:
                self.redirect('/reserve/'+key+'#signin-box')
            else:
                try:
                    p = ndb.Key(urlsafe=key).get()
                    if p.confirmed:
                        return
                    if p.key.parent() == self.user_prefs.key:
                        self.params['res'] = p.to_dict()
                        route = p.route.get()
                        self.params.update(route.to_dict(True))
                        if p.__class__.__name__ == 'OfferRequest':
                            self.params['reserve_title'] = 'Edit Reservation'
                            self.render('post/forms/fillreserve.html', **self.params)
                        else:
                            self.params['reserve_title'] = 'Edit Offer'
                            self.render('post/forms/filloffer.html', **self.params)
                except:
                   self.abort(404) 
                   return
        elif action=='route' and key:
            if not self.user_prefs:
                self.redirect('/route/'+key+'#signin-box')
            # try:
            p = ndb.Key(urlsafe=key).get()                    
            self.params.update(p.to_dict(True))
            if p.__class__.__name__ == 'Route':    # trying to reserve existing route
                self.params['res']={}
                self.params['reserve_title'] = 'Make a Reservation'
                self.render('post/forms/fillreserve.html', **self.params)
            else:           # offering to deliver
                ## check to make sure they are a driver
                d = Driver.by_userkey(self.user_prefs.key)
                if not d:
                    self.params['createorupdate'] = 'Ready to Drive'
                    self.params.update(self.user_prefs.params_fill())
                    self.render('user/forms/filldriver.html', **self.params)
                    return            
                self.params['res']={'rates':p.rates}
                self.params['reserve_title'] = 'Make a Delivery Offer'
                self.render('post/forms/filloffer.html', **self.params)     
            # except:
                # self.abort(403) 
                # return
        elif action=='jsonres' and key:
            try:
                res = ndb.Key(urlsafe=key).get()
                route = res.route.get()
            except:
                self.abort(400)
            if route.__class__.__name__=='Route':
                rdump = RouteUtils.dumproutepts(route,[res.start,res.dest])
            else:
                rdump = RouteUtils.dumproutepts(res,[route.start,route.dest])                
            self.response.headers['Content-Type'] = "application/json"                
            self.write(rdump)      
        elif key: 
            self.view_reserve_page(key)
        else:
            self.redirect('/')            
            
            
    def post(self, action=None,key=None):
        if not key:
            self.abort(400)
            return
        try:
            p = ndb.Key(urlsafe=key).get()
        except:
            self.abort(400)
            return 
        if action=='route':
            # creating a new reservation
            if p.__class__.__name__=='Route':
                self.__create_reserve(p)
            else:
                self.__create_offer(p)
        elif action=='edit':
            if p.__class__.__name__ == 'OfferRequest':
                self.__create_reserve(p.route.get(), key)
            else:
                self.__create_offer(p.route.get(), key)

        elif action=='delete' and key:
            self.__delete(key)

        elif action=='decline' and key:
            self.__decline(key)
            
        elif action=='confirm' and key:
            self.__confirm(key)            
            
        elif action=='msg' and key:
            msg = self.request.get('msg')
            try:
                p = ndb.Key(urlsafe=key).get()
                if p.__class__.__name__== 'OfferRequest':
                    subject = 'Re: Reservation Request from ' + p.sender_name()
                    body = msg + res_msg_end % key
                else:
                    subject = 'Re: Delivery Offer from ' + p.sender_name()
                    body = msg + do_msg_end % key
                # receiver needs to be the other person
                if p.driver == self.user_prefs.key:
                    receiver = p.sender
                else:
                    receiver = p.driver
                create_msg(self, sender=self.user_prefs.key, receiver=receiver, 
                                subject=subject, msg=body)
                return  
            except:
                self.abort(400) 
                return                
    def __delete(self, key=None):
        if key:
            try:
                r = ndb.Key(urlsafe=key).get()
                if r.confirmed:
                    return
                if r and self.user_prefs and self.user_prefs.key==r.key.parent():
                    post = r.route.urlsafe()
                    r.dead = PostStatus.index('DELETED')
                    r.put()
            except:
                self.abort(403) 
                return
        self.redirect('/post/'+post)
        return

    def __confirm(self, key=None):
        if key:
           # try:
            r = ndb.Key(urlsafe=key).get()
            if r: 
                if r.driver==self.user_prefs.key:
                    #Notify and send message
                    n = r.sender.get().get_notify()
                    msg = self.user_prefs.first_name + confirm_res_msg % key
                    create_note(self, r.sender, confirm_res_sub, msg)
                    # create associated tracker
                    create_from_res(r)
                    # charge the cc
                    self.redirect('/checkout/confirmhold/'+key)
                    return
                else:
                    # go to checkout
                    d = Driver.by_userkey(r.driver)
                    self.params['d'] = d.params_fill()
                    self.params['reskey'] = key
                    self.params.update(r.to_dict())
                    self.params['checkout_action'] = '/checkout/confirm/'+key
                    self.render('launch/checkout.html', **self.params)
                    return
            # except:
                # self.abort(400) 
                # return
        self.abort(403)
        return
        
    def __decline(self, key=None):
        if key:
            try:
                r = ndb.Key(urlsafe=key).get()
                if r:
                    if r.driver==self.user_prefs.key:
                        msg = self.user_prefs.first_name + decline_res_msg
                        msg = msg + r.print_html()
                        create_note(self, r.sender, decline_res_sub, msg)
                    else:
                        msg = self.user_prefs.first_name + decline_do_msg
                        msg = msg + r.print_html()
                        create_note(self, r.sender, decline_do_sub, msg)
                    routekey=r.route.urlsafe()
                    r.dead = PostStatus.index('DECLINED')
                    r.put()
                    self.redirect('/post/'+routekey)
                    return
            except:
                self.abort(403) 
                return
        self.abort(403)
        return                
                
    def __create_offer(self, route, res=None):
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        msg = self.request.get('msg')
        dropoff = bool(int(self.request.get('dropoff')))
        pickup = bool(int(self.request.get('pickup')))
        delivok = bool(int(self.request.get('delivok')))        
        repost= bool(self.request.get('repost'))
        
        if delivok:
            reqdate = self.request.get('reqdate')
            reqdate = parse_date(reqdate)
        else:
            reqdate = route.delivby
        if dropoff:
            start, startstr = self.__get_map_form('start')
        else:
            startstr = route.locstart
            start = route.start
        if pickup:
            dest, deststr = self.__get_map_form('dest')
        else:
            deststr = route.locend 
            dest = route.dest
          
        # try:
        if not res:
            p = OfferRoute(parent=self.user_prefs.key,
            route = route.key,
            driver=self.user_prefs.key, sender=route.key.parent(), 
            rates=rates, pickup=pickup, dropoff=dropoff, 
            start=start, dest=dest,
            locstart=startstr, locend=deststr, deliverby=reqdate)
            new_res = True
        else:  #editing reservation
            new_res = False
            p = ndb.Key(urlsafe=res).get()            
            if p.confirmed:
                self.params['permission_err'] = True
                self.params.update(route.get().to_dict(True))
                self.render('post/forms/filloffer.html', **self.params)
                return
            if p and self.user_prefs and p.driver == self.user_prefs.key:  
                p.rates = rates
                p.deliverby = reqdate
                p.pickup = pickup
                p.dropoff = dropoff
                p.locstart = startstr
                p.locend = deststr
                p.start = start
                p.dest = dest
                
        if new_res and repost:
            p.repost = route_from_off(p)                                    
        # except:
            # self.abort(403)
            # return  

        if msg:
            create_message(self, route, None, route.key.parent(), self.user_prefs.key, msg)
        try:
            p.put() 
            if new_res:
                do_msg = new_do_msg % p.key.urlsafe()
                create_note(self, route.key.parent(), new_do_sub, do_msg)
                logging.info('New Offer: '+ p.key.urlsafe())
                route.offers.append(p.key)
                route.put()
            self.redirect('/reserve/' + p.key.urlsafe())      
        except:
            self.params['error_route'] = 'Invalid Dropoff or Pickup Location'
            self.params['pickup'] = int(pickup)
            self.params['dropoff'] = int(dropoff)
            self.params['reqdate'] = reqdate
            self.params['offer'] = rates
            self.params['msg'] = msg
            self.params['reserve_title'] = 'Edit Offer'
            self.params['res']=route.to_dict(True)
            self.render('post/forms/filloffer.html', **self.params)                                 
    
    def __create_reserve(self, route, res=None):
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        items = self.request.get('items')
        dropoff = bool(int(self.request.get('dropoff')))
        pickup = bool(int(self.request.get('pickup')))
        repost= bool(self.request.get('repost'))
        img = self.request.get("file")       
        
        reqdate = route.delivend
        if dropoff:
            startstr = route.locstart
            start = route.start
        else:
            start, startstr = self.__get_map_form('start')
        if pickup:
            deststr = route.locend 
            dest = route.dest
        else:
            dest, deststr = self.__get_map_form('dest')
        try:
            if not res:
                new_res = True
                p = OfferRequest(parent=self.user_prefs.key, 
                sender=self.user_prefs.key, driver=route.key.parent(), 
                route=route.key)
            else:  #editing reservation
                new_res = False
                p = ndb.Key(urlsafe=res).get()
                if p.confirmed:
                    self.params['permission_err'] = True
                    self.params.update(route.get().to_dict(True))
                    self.render('post/forms/fillreserve.html', **self.params)
                    return
            if p and self.user_prefs and p.sender == self.user_prefs.key:  
                p.rates = rates
                p.details = items
                p.deliverby = reqdate
                p.pickup = pickup
                p.dropoff = dropoff                
                p.locstart = startstr
                p.locend = deststr
                p.start = start
                p.dest = dest
                if img:
                    imgstore = ImageStore.new(img)
                    imgstore.put()
                    p.img_id = imgstore.key.id()
                if new_res and repost:
                    p.repost = request_from_off(p)                    
        except:
            self.abort(403)
            return  
                            
        try:
            p.put()             
            taskqueue.add(url='/summary/selfnote/'+p.key.urlsafe(), method='get')
        except:
            logging.error(p)
            self.params['error_route'] = 'Invalid Start or Destination'
            self.params['pickup'] = int(pickup)
            self.params['dropoff'] = int(dropoff)
            self.params['details'] = items
            self.params['offer'] = rates
            self.params['reserve_title'] = 'Edit Reservation'
            self.params.update(route.get().to_dict(True))
            self.render('post/forms/fillreserve.html', **self.params)

        if new_res:
            route.offers.append(p.key)
            route.put()                    
        # Do they have a credit card on file?
        if not self.user_prefs.cc:
            self.params.update(self.user_prefs.params_fill())
            self.params['next_url'] = '/reserve/' + p.key.urlsafe()
            self.params['get_info'] = True
            self.render('money/forms/cc.html', **self.params)
            return            
             
        self.redirect('/reserve/' + p.key.urlsafe())  
            
    def view_reserve_page(self,key):
        p = ndb.Key(urlsafe=key).get()
        self.params['confirm_allow'] = False
        self.params['is_receiver'] = False
        self.params['is_sender'] = False        
        if p:
            route = p.route.get()
            self.params['message_url'] = route.message_url()
            self.params['post_url'] = route.post_url()
            self.params['first_name'] = route.first_name()
            resoffer=(p.__class__.__name__ == 'OfferRequest')
            self.params['res'] = p.to_dict()
            if resoffer:
                self.params.update(p.sender.get().params_fill_sm())
            else:
                self.params.update(p.driver.get().params_fill_sm())
            self.params['edit_allow'] = False
            
            if self.user_prefs and self.user_prefs.key==p.key.parent():
                self.params['is_sender'] = True                
                if p.dead==0:
                    self.params['edit_allow'] = True
                
            elif self.user_prefs and (self.user_prefs.key==p.driver or self.user_prefs.key==p.sender):
                self.params['is_receiver'] = True
                if p.dead==0:
                    self.params['confirm_allow'] = True
                
        else:
            #see if it's expired
            #TODO: create a receipt page
            self.abort(409)
        if resoffer:
            self.render('post/reserve.html', **self.params)
        else:
            self.render('post/offer.html', **self.params)    
            
    def __get_map_form(self,pt):
        ptlat = self.request.get(pt+'lat')
        ptlon = self.request.get(pt+'lon')
        ptstr = self.request.get(pt+'str')        
        if not ptstr or not ptlat or not ptlon:
            ptstr = self.request.get(pt)
            if ptstr:
                ptg = RouteUtils.getGeoLoc(ptstr)[0]
            else:
                ptg = None
        else:
            ptg = ndb.GeoPt(lat=ptlat,lon=ptlon)    
        return ptg, ptstr       
        
def request_from_off(res):
    if not res.repost:
        if res.has_cc:
            rs = ReqStats(status = RequestStatus.index('PURSUE'))
        else:
            rs = ReqStats(status = RequestStatus.index('NO_CC'))
        r = Request(parent=res.key.parent(), stats=rs) 
    else:
        r = res.repost.get()
    r.details=res.details
    r.start=res.start
    r.dest=res.dest
    r.locstart=res.locstart
    r.locend=res.locend
    r.rates=res.rates
    r.delivby=res.deliverby
    r.img_id=res.img_id
    return r.put()
    
def route_from_off(res):
    if not res.repost:
        r = Route(parent=res.key.parent()) 
    else:
        r = res.repost.get()    
    r.start=res.start
    r.dest=res.dest
    r.locstart=res.locstart
    r.locend=res.locend
    r.delivend=res.deliverby
    r.delivstart=res.deliverby
    return r.put()    