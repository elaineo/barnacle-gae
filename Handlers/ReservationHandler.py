from datetime import *
from google.appengine.ext import ndb

from Handlers.BaseHandler import *
from Handlers.Launch.CheckoutHandler import *
from Handlers.RouteHandler import fill_route_params
from Handlers.Tracker.TrackerHandler import create_from_res
from Handlers.MessageHandler import create_message
from Models.Post.OfferRequest import *
from Models.Post.OfferRoute import *
from Models.User.Driver import *
from Utils.RouteUtils import *
from Utils.ValidUtils import *
from Utils.EmailUtils import create_note
from Utils.Defs import *
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
                        if p.__class__.__name__ == 'OfferRequest':
                            self.params.update(fill_route_params(p.route.urlsafe(),True))                            
                            self.params['reserve_title'] = 'Edit Reservation'
                            self.render('post/forms/fillreserve.html', **self.params)
                        else:
                            self.params.update(fill_route_params(p.route.urlsafe(),False))
                            self.params['reserve_title'] = 'Edit Offer'
                            self.render('post/forms/filloffer.html', **self.params)
                except:
                   self.abort(404) 
                   return
        elif action=='route' and key:
            if not self.user_prefs:
                self.redirect('/post/'+key+'#signin-box')
            try:
                p = ndb.Key(urlsafe=key).get()            
                if p.__class__.__name__ == 'Route':    # trying to reserve existing route
                    self.params['res']={}
                    self.params.update(fill_route_params(key,True))
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
                    self.params['res']={'price':p.rates}
                    self.params.update(fill_route_params(key,False))
                    self.params['reserve_title'] = 'Make a Delivery Offer'
                    self.render('post/forms/filloffer.html', **self.params)     
            except:
                self.abort(403) 
                return
        elif action=='jsonres' and key:
            try:
                res = ndb.Key(urlsafe=key).get()
                route = res.route.get()
            except:
                self.abort(400)
            if route.__class__.__name__=='Route':
                rdump = RouteUtils().dumproutepts(route,[res.start,res.dest])
            else:
                rdump = RouteUtils().dumproutepts(res,[route.start,route.dest])                
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
                if r and r.sender==self.user_prefs.key:
                    post = r.route.urlsafe()
                    r.key.delete()
                    self.redirect('/post/'+post)
                    return
            except:
                self.abort(403) 
                return
        self.abort(403)
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
            price=rates, pickup=pickup, dropoff=dropoff, 
            start=start, dest=dest,
            locstart=startstr, locend=deststr, deliverby=reqdate)
            new_res = True
        else:  #editing reservation
            new_res = False
            p = ndb.Key(urlsafe=res).get()
            if p.confirmed:
                self.params['permission_err'] = True
                self.params.update(fill_route_params(route.key.urlsafe(),False))
                self.render('post/forms/filloffer.html', **self.params)
                return
            if p and self.user_prefs and p.driver == self.user_prefs.key:  
                p.price = rates
                p.deliverby = reqdate
                p.pickup = pickup
                p.dropoff = dropoff
                p.locstart = startstr
                p.locend = deststr
                p.start = start
                p.dest = dest
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
            self.params.update(fill_route_params(route.key.urlsafe(),False))
            self.render('post/forms/filloffer.html', **self.params)                                 
    
    def __create_reserve(self, route, res=None):
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        items = self.request.get('items')
        dropoff = bool(int(self.request.get('dropoff')))
        pickup = bool(int(self.request.get('pickup')))
        reqdate = self.request.get('reqdate')
        
        if reqdate:
            reqdate = parse_date(reqdate)
        else:
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
                route=route.key, details=items, price=rates, deliverby=reqdate, 
                start=start, dest=dest,
                pickup=pickup, dropoff=dropoff, locstart=startstr, locend = deststr)
            else:  #editing reservation
                new_res = False
                p = ndb.Key(urlsafe=res).get()
                if p.confirmed:
                    self.params['permission_err'] = True
                    self.params.update(fill_route_params(route.key.urlsafe(),True))
                    self.render('post/forms/fillreserve.html', **self.params)
                    return
                if p and self.user_prefs and p.sender == self.user_prefs.key:  
                    p.price = rates
                    p.details = items
                    p.deliverby = reqdate
                    p.pickup = pickup
                    p.dropoff = dropoff                
                    p.locstart = startstr
                    p.locend = deststr
                    p.start = start
                    p.dest = dest
        except:
            self.abort(403)
            return  
                            
        try:
            p.put()             
        except:
            self.params['error_route'] = 'Invalid Start or Destination'
            self.params['pickup'] = int(pickup)
            self.params['dropoff'] = int(dropoff)
            self.params['details'] = items
            self.params['reqdate'] = reqdate
            self.params['offer'] = rates
            self.params['msg'] = msg
            self.params['reserve_title'] = 'Edit Reservation'
            self.params.update(fill_route_params(route.key.urlsafe(),True))
            self.render('post/forms/fillreserve.html', **self.params)

        if new_res:
            d = Driver.by_userkey(p.driver)
            self.params['d'] = d.params_fill()
            self.params['reskey'] = p.key.urlsafe()
            self.params.update(p.to_dict())
            self.params['checkout_action'] = '/checkout/hold/'+p.key.urlsafe()
            logging.info('New Reservation: '+ p.key.urlsafe())
            self.render('post/reservation.html', **self.params)
            route.offers.append(p.key)
            route.put()            
        else:
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
            logging.info(p.to_dict())
            self.params['edit_allow'] = False
            
            if self.user_prefs and self.user_prefs.key==p.key.parent():
                self.params['is_sender'] = True                
                if not p.confirmed:
                    self.params['edit_allow'] = True
                
            elif self.user_prefs and (self.user_prefs.key==p.driver or self.user_prefs.key==p.sender):
                self.params['is_receiver'] = True
                if not p.confirmed:
                    self.params['confirm_allow'] = True
                
        else:
            #see if it's expired
            #TODO: create a receipt page
            if p.dead>0:
                logging.info('Expired offer')
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
                ptg = RouteUtils().getGeoLoc(ptstr)[0]
            else:
                ptg = None
        else:
            ptg = ndb.GeoPt(lat=ptlat,lon=ptlon)    
        return ptg, ptstr       