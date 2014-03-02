from google.appengine.ext import ndb
from Models.Post.Post import PostStatus

""" Base class for Offers - Reservations or Delivery Offers """
""" Parent will be the user """
""" key is added to Post.offers"""

dropoffstr_1 = 'Sender will drop off at start.'
dropoffstr_0 = 'Driver will pick up at start.'
pickupstr_1 = 'Sender will pick up at destination.'
pickupstr_0 = 'Driver will deliver to destination.'

class Offer(ndb.Model):
    """ Make a Reservation for existing route """
    route = ndb.KeyProperty(required=True)
    sender = ndb.KeyProperty(required=True)      # this is the sender
    driver = ndb.KeyProperty(required=True)    # this is the driver
    rates = ndb.IntegerProperty()   # Offer price
    created = ndb.DateTimeProperty(auto_now_add=True)
    deliverby = ndb.DateProperty(required=True)
    pickup = ndb.BooleanProperty(default=False)     # sender picks up shit at dest
    dropoff = ndb.BooleanProperty(default=True)     # sender drops off shit at start
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location
    confirmed = ndb.BooleanProperty(default=False)
    repost = ndb.KeyProperty()      #corresponding route or request
    dead = ndb.IntegerProperty(default=0)    # see PostStatus   
            
    def post_url(self):
        """ url for public view of reservation """
        return '/reserve/' + self.key.urlsafe()

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

    def driver_name(self):
        return self.driver.get().nickname()        

    @classmethod
    def by_user(cls,userkey,dead=0):
        return cls.query(cls.dead==dead, ancestor=userkey)
        
    @classmethod
    def by_sender(cls,userkey,dead=0):
        return cls.query(cls.sender==userkey, cls.dead==dead)

    @classmethod
    def by_driver(cls,userkey,dead=0):
        return cls.query(cls.driver==userkey, cls.dead==dead)

    @classmethod
    def by_route(cls,rkey,dead=0):
        return cls.query(cls.route==rkey,cls.dead==dead)

    @classmethod
    def route_confirmed(cls,rkey):
        q = cls.query(cls.confirmed==True, cls.route==rkey).count()
        return q
    
    def base_dict(cls):
        u = cls.key.parent().get()
        route = {
            'routekey' : cls.route.urlsafe(),
            'first_name' : u.nickname(),
            'profile_url' : u.profile_url(),
            'edit_url' : cls.edit_url(),
            'confirm_url': cls.confirm_url(),
            'delete_url' : cls.delete_url(),
            'decline_url' : cls.decline_url(),
            'reservekey' : cls.key.urlsafe(),
            'reserve_url' : cls.post_url(),
            'delivby' : cls.deliverby.strftime('%m/%d/%Y'),
            'sender' : cls.sender_name(),
            'driver' : cls.driver_name(),
            'rates' : cls.rates,
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'confirmed' : cls.confirmed,
            'pickup' : int(cls.pickup),
            'dropoff' : int(cls.dropoff)
        }
        if cls.dropoff:
            route['dropoffstr'] = dropoffstr_1 
        else:
            route['dropoffstr'] = dropoffstr_0 
        if cls.pickup: 
            route['pickupstr'] = pickupstr_1 
        else:
            route['pickupstr'] = pickupstr_0
        if cls.confirmed:
            route['track_url'] = '/track/view/' ##TODO: Figure this out
        if cls.dead > 0:
            route['status'] = PostStatus[cls.dead]
        else:
            route['status'] = ''
        return route        
        
class ExpiredOffer(ndb.Model):
    """ Make an offer to deliver """
    sender = ndb.KeyProperty()      # user_prefs of reserver and reservee
    receiver = ndb.KeyProperty()
    route = ndb.KeyProperty()       # route being reserved
    oldkey = ndb.KeyProperty()
    price = ndb.IntegerProperty()   # Offer price
    locstart = ndb.StringProperty() 
    locend = ndb.StringProperty()        
    sender_name = ndb.StringProperty() 
    rcvr_name = ndb.StringProperty() 
    deliverby = ndb.DateProperty()
    confirmed = ndb.BooleanProperty(default=False)        