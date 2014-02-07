from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Models.Tracker.TrackerModel import *
from Utils.RouteUtils import *

dropoffstr_1 = 'Sender will drop off at start.'
dropoffstr_0 = 'Driver will pick up at start.'
pickupstr_1 = 'Sender will pick up at destination.'
pickupstr_0 = 'Driver will deliver to destination.'

class Reservation(ndb.Model):
    """ Make a Reservation for existing route """
    sender = ndb.KeyProperty(required=True)      # this is the sender
    receiver = ndb.KeyProperty(required=True)    # this is the driver
    route = ndb.KeyProperty(required=True)       # route being reserved
    items = ndb.TextProperty()    # description of goods
    price = ndb.IntegerProperty()   # Offer price
    created = ndb.DateTimeProperty(auto_now_add=True)
    deliverby = ndb.DateProperty(required=True)
    pickup = ndb.BooleanProperty(default=False)     # sender picks up shit at dest
    dropoff = ndb.BooleanProperty(default=True)     # sender drops off shit at start
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location
    confirmed = ndb.BooleanProperty(default=False)
    img_id = ndb.IntegerProperty()     
            
    def reserve_url(self):
        """ url for public view of reservation """
        return '/reserve/' + self.key.urlsafe()
    def track_url(self):
        """ if confirmed url for tracking page """
        t = TrackerModel.by_reservation(self.key).get()
        if t:
            return t.post_url()
        else:
            return ''
    def edit_url(self):
        """ url for editing reservation"""
        return '/reserve/edit/' + self.key.urlsafe()
    def confirm_url(self):
        """ url for confirming reservation"""
        return '/reserve/confirm/' + self.key.urlsafe()        
    def delete_url(self):
        """ url for deleting reservation"""
        return '/reserve/delete/' + self.key.urlsafe()
    def decline_url(self):
        """ url for declining reservation"""
        return '/reserve/decline/' + self.key.urlsafe()        
    def message_url(self):
        """ url for adding message"""
        return '/message/route/' + self.route.urlsafe()
    def sender_name(self):
        return self.sender.get().nickname()
    def receiver_name(self):
        return self.receiver.get().nickname()        
    @classmethod
    def by_sender(cls,userkey,confirmed=False):
        if confirmed:
            return cls.query().filter(ndb.AND(cls.sender==userkey, cls.confirmed==True))
        else:
            return cls.query().filter(cls.sender==userkey)
    @classmethod
    def by_receiver(cls,userkey):
        return cls.query().filter(cls.receiver==userkey)
    @classmethod
    def by_route(cls,rkey):
        return cls.query().filter(cls.route==rkey)

    @classmethod
    def route_confirmed(cls,rkey):
        q = cls.query().filter(cls.route==rkey, cls.confirmed==True).count()
        return q
    
    def to_dict(cls):
        route = {
            'reserve_url' : cls.reserve_url(),
            'delivby' : cls.deliverby.strftime('%m/%d/%Y'),
            'sender' : cls.sender_name(),
            'receiver' : cls.receiver_name(),
            'price' : cls.price,
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'confirmed' : cls.confirmed,
            'pickup' : cls.pickup,
            'dropoff' : cls.dropoff
        }
        if cls.dropoff:
            route.update( { 'dropoffstr' : dropoffstr_1 } )
        else:
            route.update( { 'dropoffstr' : dropoffstr_0 } )
        if cls.pickup: 
            route.update( { 'pickupstr' : pickupstr_1 } )
        else:
            route.update( { 'pickupstr' : pickupstr_0 } )        
        return route
        
    def print_html(cls):
        rout = cls.receiver_name() + '\'s route from ' + cls.locstart + ' to ' + cls.locend
        rout += '\nDeliver By: ' + cls.deliverby.strftime('%m/%d/%Y')
        rout += '\nItems: ' + cls.items
        rout += '\nOffer price: ' + str(cls.price)
        return rout
        
class DeliveryOffer(ndb.Model):
    """ Make an offer to deliver """
    sender = ndb.KeyProperty()      # this is the driver
    receiver = ndb.KeyProperty()    # this is the sender. I should have planned this better
    route = ndb.KeyProperty()       # route being reserved
    price = ndb.IntegerProperty()   # Offer price
    pickup = ndb.BooleanProperty(default=False)     # sender picks up shit at dest
    dropoff = ndb.BooleanProperty(default=True)     # sender drops off shit at start
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location    
    created = ndb.DateTimeProperty(auto_now_add=True)
    deliverby = ndb.DateProperty()
    confirmed = ndb.BooleanProperty(default=False)
    pathpts = ndb.GeoPtProperty(repeated=True)         
   
            
    def reserve_url(self):
        """ url for public view of reservation """
        return '/reserve/' + self.key.urlsafe()
    def track_url(self):
        """ if confirmed url for tracking page """
        t = TrackerModel.by_reservation(self.key).get()
        if t:
            return t.get().post_url()
        else:
            return ''        
    def edit_url(self):
        """ url for editing reservation"""
        return '/reserve/edit/' + self.key.urlsafe()
    def confirm_url(self):
        """ url for confirming reservation"""
        return '/reserve/confirm/' + self.key.urlsafe()
    def delete_url(self):
        """ url for deleting offer"""
        return '/reserve/delete/' + self.key.urlsafe()
    def decline_url(self):
        """ url for declining reservation"""
        return '/reserve/decline/' + self.key.urlsafe()                
    def message_url(self):
        """ url for adding message"""
        return '/message/route/' + self.route.urlsafe()
    def sender_name(self):
        return self.sender.get().nickname()
    def receiver_name(self):
        return self.receiver.get().nickname()                
    @classmethod
    def by_sender(cls,userkey):
        return cls.query().filter(cls.sender==userkey)
    @classmethod
    def by_receiver(cls,userkey,confirmed=False):
        if confirmed:
            return cls.query().filter(ndb.AND(cls.receiver==userkey,cls.confirmed==True))
        else:
            return cls.query().filter(cls.receiver==userkey)            
    @classmethod
    def by_route(cls,rkey):
        return cls.query().filter(cls.route==rkey)
    @classmethod
    def route_confirmed(cls,rkey):
        q = cls.query().filter(cls.route==rkey, cls.confirmed==True).count()
        return q
        
    def to_dict(cls):
        route = {
            'reserve_url' : cls.reserve_url(),
            'delivby' : cls.deliverby.strftime('%m/%d/%Y'),
            'sender' : cls.sender_name(),
            'receiver' : cls.receiver_name(),
            'locstart' : cls.locstart,
            'locend' : cls.locend,            
            'price' : cls.price,
            'confirmed' : cls.confirmed            
        }
        if cls.dropoff:
            route.update( { 'dropoffstr' : dropoffstr_1 } )
        else:
            route.update( { 'dropoffstr' : dropoffstr_0 } )
        if cls.pickup: 
            route.update( { 'pickupstr' : pickupstr_1 } )
        else:
            route.update( { 'pickupstr' : pickupstr_0 } )             
        return route
        
    def print_html(cls):
        rout = cls.receiver_name() + '\'s Delivery Request'
        rout += '\nDeliver By: ' + cls.deliverby.strftime('%m/%d/%Y')
        rout += '\nOffer price: ' + str(cls.price)
        return rout        
        
class ExpiredReservation(ndb.Model):
    """ Make a Reservation for existing route """
    sender = ndb.KeyProperty()      # user_prefs of reserver and reservee
    receiver = ndb.KeyProperty()
    route = ndb.KeyProperty()       # route being reserved
    price = ndb.IntegerProperty()   # Offer price
    deliverby = ndb.DateProperty()
    locstart = ndb.StringProperty() 
    locend = ndb.StringProperty()    
    sender_name = ndb.StringProperty() 
    rcvr_name = ndb.StringProperty()     
    items = ndb.TextProperty()    # description of goods
    confirmed = ndb.BooleanProperty(default=False)
    img_id = ndb.IntegerProperty()     
    
    @classmethod
    def deliveries_completed(cls, rcvr):
        r = cls.query().filter(cls.receiver==rcvr)
        return r.count()
    @classmethod        
    def deliveries_sent(cls, sender):
        r = cls.query().filter(cls.sender==sender)
        return r.count()

    @classmethod
    def by_sender(cls,userkey):
        return cls.query().filter(cls.sender==userkey)
    @classmethod
    def by_receiver(cls,userkey):
        return cls.query().filter(cls.receiver==userkey)
    @classmethod
    def by_user(cls,userkey):
        return cls.query().filter(ndb.OR(cls.receiver==userkey,cls.sender==userkey))
    @classmethod
    def by_route(cls,key):
        return cls.query().filter(cls.route==key)
        
    def to_dict(cls):
        res = {
            'senderkey': cls.sender.urlsafe(),
            'receiverkey': cls.receiver.urlsafe(),
            'route': cls.route.urlsafe(),
            'price' : cls.price,
            'deliverby' : cls.deliverby.strftime('%m/%d/%Y'),
            'locstart': cls.locstart,
            'locend': cls.locend,
            'sender_name':cls.sender_name,
            'receiver_name':cls.rcvr_name
        }
        return res
        
class ExpiredOffer(ndb.Model):
    """ Make an offer to deliver """
    sender = ndb.KeyProperty()      # user_prefs of reserver and reservee
    receiver = ndb.KeyProperty()
    route = ndb.KeyProperty()       # route being reserved
    price = ndb.IntegerProperty()   # Offer price
    locstart = ndb.StringProperty() 
    locend = ndb.StringProperty()        
    sender_name = ndb.StringProperty() 
    rcvr_name = ndb.StringProperty() 
    deliverby = ndb.DateProperty()
    confirmed = ndb.BooleanProperty(default=False)
    
    def to_dict(cls):
        r = cls.route.get()
        res = {
            'senderkey': cls.receiver.urlsafe(),
            'receiverkey': cls.sender.urlsafe(),
            'route': cls.route.urlsafe(),
            'locstart': cls.locstart,
            'locend': cls.locend,
            'sender_name':cls.rcvr_name,
            'receiver_name':cls.sender_name, 
            'price' : cls.price,
            'deliverby' : cls.deliverby.strftime('%m/%d/%Y')
        }
        return res
    
    @classmethod        
    def deliveries_completed(cls, sender):
        r = cls.query().filter(cls.sender==sender)
        return r.count()
    @classmethod
    def deliveries_sent(cls, rcvr):
        r = cls.query().filter(cls.receiver==rcvr)
        return r.count()        
    @classmethod
    def by_sender(cls,userkey):
        return cls.query().filter(cls.sender==userkey)
    @classmethod
    def by_receiver(cls,userkey):
        return cls.query().filter(cls.receiver==userkey)        
    @classmethod
    def by_user(cls,userkey):
        return cls.query().filter(ndb.OR(cls.receiver==userkey,cls.sender==userkey))        