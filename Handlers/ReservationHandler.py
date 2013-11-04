from datetime import *
from google.appengine.ext import ndb

from Handlers.BaseHandler import *
from Handlers.Launch.CheckoutHandler import *
from Handlers.RouteHandler import fill_route_params
from Handlers.Tracker.TrackerHandler import create_from_res
from Models.ReservationModel import *
from Models.Launch.Driver import *
from Utils.RouteUtils import *
from Utils.ValidUtils import *
from Utils.EmailUtils import create_note, create_msg
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
                    if p.sender == self.user_prefs.key:
                        if p.__class__.__name__ == 'Reservation':
                            self.params.update(fill_route_params(p.route.urlsafe(),True))
                            self.params.update(fill_reserve_params(key,True))
                            self.params['reserve_title'] = 'Edit Reservation'
                            self.render('forms/fillreserve.html', **self.params)
                        else:
                            self.params.update(fill_route_params(p.route.urlsafe(),False))
                            self.params.update(fill_reserve_params(key,False))
                            self.params['reserve_title'] = 'Edit Offer'
                            self.render('forms/filloffer.html', **self.params)                    
                except:
                   self.abort(404) 
                   return
        elif action=='route' and key:
            if not self.user_prefs:
                self.redirect('/post/'+key+'#signin-box')
            try:
                p = ndb.Key(urlsafe=key).get()
                if p.__class__.__name__ == 'Route':    # trying to reserve existing route
                    self.params.update(fill_route_params(key,True))
                    self.params['reserve_title'] = 'Make a Reservation'
                    self.render('forms/fillreserve.html', **self.params)
                else:           # offering to deliver
                    self.params.update(fill_route_params(key,False))
                    self.params['reserve_title'] = 'Make a Delivery Offer'
                    self.params['offer'] = p.rates
                    self.render('forms/filloffer.html', **self.params)     
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
            if p.__class__.__name__ == 'Reservation':
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
                if p.__class__.__name__== 'Reservation':
                    subject = 'Re: Reservation Request from ' + p.sender_name()
                    body = msg + res_msg_end % key
                else:
                    subject = 'Re: Delivery Offer from ' + p.sender_name()
                    body = msg + do_msg_end % key
                # receiver needs to be the other person
                if p.receiver == self.user_prefs.key:
                    receiver = p.sender
                else:
                    receiver = p.receiver
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
            if r and r.receiver==self.user_prefs.key:
                if r.__class__.__name__== 'Reservation':
                    #Notify and send message
                    n = r.sender.get().get_notify()
                    if 1 in n:
                        msg = self.user_prefs.first_name + confirm_res_msg % key
                        create_note(r.sender, confirm_res_sub, msg)
                    # create associated tracker
                    create_from_res(r)
                    # charge the cc
                    self.redirect('/checkout/confirmhold/'+key)
                    return
                else:
                    # go to checkout
                    d = Driver.by_userkey(r.sender)
                    self.params['d'] = d.params_fill({})
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
                if r and r.receiver==self.user_prefs.key:
                    #Notify and send message
                    n = r.sender.get().get_notify()
                    if 1 in n:
                        if r.__class__.__name__== 'Reservation':
                            msg = self.user_prefs.first_name + decline_res_msg
                            msg = msg + r.print_html()
                            create_note(r.sender, decline_res_sub, msg)
                        else:
                            msg = self.user_prefs.first_name + decline_do_msg
                            msg = msg + r.print_html()
                            create_note(r.sender, decline_do_sub, msg)
                    routekey=r.route.urlsafe()
                    r.key.delete()                
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
          
        try:
            if not res:
                p = DeliveryOffer(sender=self.user_prefs.key, receiver=route.userkey, 
                route=route.key, price=rates, pickup=pickup, dropoff=dropoff, 
                start=start, dest=dest,
                locstart=startstr, locend=deststr, deliverby=reqdate)
                new_res = True
            else:  #editing reservation
                new_res = False
                p = ndb.Key(urlsafe=res).get()
                if p.confirmed:
                    self.params['permission_err'] = True
                    self.params.update(fill_route_params(route.key.urlsafe(),False))
                    self.render('forms/filloffer.html', **self.params)
                    return
                if p and self.user_prefs and p.sender == self.user_prefs.key:  
                    p.price = rates
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

        if msg:
            subject = 'Delivery Offer from ' + self.user_prefs.nickname()
            create_msg(self, sender=self.user_prefs.key, receiver=route.userkey, 
                            subject=subject, msg=msg)
        try:
            p.put() 
            if new_res:
                do_msg = new_do_msg % p.key.urlsafe()
                create_note(route.userkey, new_do_sub, do_msg)
                logging.info('New Offer: '+ p.key.urlsafe())
            self.redirect('/reserve/' + p.key.urlsafe())      
        except:
            self.params['error_route'] = 'Invalid Dropoff or Pickup Location'
            self.params['pickup'] = int(pickup)
            self.params['dropoff'] = int(dropoff)
            self.params['reqdate'] = reqdate
            self.params['offer'] = rates
            self.params['msg'] = msg
            self.params['route_title'] = 'Edit Offer'
            self.params.update(fill_route_params(route.key.urlsafe(),False))
            self.render('forms/filloffer.html', **self.params)                                 
    
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
                p = Reservation(sender=self.user_prefs.key, receiver=route.userkey, 
                route=route.key, items=items, price=rates, deliverby=reqdate, 
                start=start, dest=dest,
                pickup=pickup, dropoff=dropoff, locstart=startstr, locend = deststr)
            else:  #editing reservation
                new_res = False
                p = ndb.Key(urlsafe=res).get()
                if p.confirmed:
                    self.params['permission_err'] = True
                    self.params.update(fill_route_params(route.key.urlsafe(),True))
                    self.render('forms/fillreserve.html', **self.params)
                    return
                if p and self.user_prefs and p.sender == self.user_prefs.key:  
                    p.price = rates
                    p.items = items
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
            self.params['items'] = items
            self.params['reqdate'] = reqdate
            self.params['offer'] = rates
            self.params['msg'] = msg
            self.params['route_title'] = 'Edit Reservation'
            self.params.update(fill_route_params(route.key.urlsafe(),True))
            self.render('forms/fillreserve.html', **self.params)

        if new_res:
            d = Driver.by_userkey(p.receiver)
            self.params['d'] = d.params_fill({})
            self.params['reskey'] = p.key.urlsafe()
            self.params.update(fill_reserve_params(p.key.urlsafe(),True))
            self.params.update(p.to_dict())
            self.params['checkout_action'] = '/checkout/hold/'+p.key.urlsafe()
            logging.info('New Reservation: '+ p.key.urlsafe())
            self.render('launch/reservation.html', **self.params)            
        else:
            self.redirect('/reserve/' + p.key.urlsafe())  
            
    def view_reserve_page(self,key):
        # try:
        p = ndb.Key(urlsafe=key).get()
        resoffer=(p.__class__.__name__ == 'Reservation')
        self.params.update(fill_reserve_params(key,resoffer))
        if self.user_prefs and self.user_prefs.key == p.sender and not p.confirmed:
            self.params['edit_allow'] = True
        else:
            self.params['edit_allow'] = False
        self.params['confirm_allow'] = False
        self.params['is_receiver'] = False
        self.params['is_sender'] = False
        if self.user_prefs and self.user_prefs.key == p.receiver:
            self.params['is_receiver'] = True
            if not p.confirmed:
                self.params['confirm_allow'] = True
        if self.user_prefs and self.user_prefs.key == p.sender:                
            self.params['is_sender'] = True
        if resoffer:
            self.render('reserve.html', **self.params)
        else:
            self.render('offer.html', **self.params)
        # except:
            # self.abort(409)
            # return       
            
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
            
def fill_reserve_params(key,resoffer=False):
    p = ndb.Key(urlsafe=key).get()
    r = p.route.get()
    u = p.sender.get()
    o = p.receiver.get()
    params = {
        'sender_profile_url' : u.profile_url(),
        'sender_prof_thumb': u.profile_image_url('small'),
        'receiver_profile_url' : o.profile_url(),
        'receiver_prof_thumb': o.profile_image_url('small'),
        'sender_first_name': u.nickname(),
        'sender_last_name': u.last_name,
        'receiver_first_name': o.nickname(),
        'receiver_last_name': o.last_name,
        'offer': p.price,
        'reqdate' : p.deliverby.strftime('%m/%d/%Y'),
        'confirmed' : p.confirmed,
        'pickup' : int(p.pickup),
        'dropoff' : int(p.dropoff), 
        'reqstart' : p.locstart,
        'reqend' : p.locend,
        'post_url' : r.post_url(),
        'edit_url' : p.edit_url(),
        'delete_url':p.delete_url(),
        'decline_url':p.decline_url(),
        'confirm_url':p.confirm_url(),
        'send_message_url': p.send_message_url(),
        'reservekey' : key,
        'msg_ok' : True #(0 in u.get_notify() and 0 in o.get_notify())
        }
    if p.dropoff:
        params.update( { 'dropoffstr' : dropoffstr_1 } )
    else:
        params.update( { 'dropoffstr' : dropoffstr_0 } )
    if p.pickup: 
        params.update( { 'pickupstr' : pickupstr_1 } )
    else:
        params.update( { 'pickupstr' : pickupstr_0 } )
    if resoffer:
        params.update( {'items' : p.items })
    else:
        params.update( {'delivok' : int(p.deliverby != r.delivby) })
    if p.confirmed:
        params['track_url'] = p.track_url()
    return params