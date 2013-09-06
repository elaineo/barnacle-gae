from google.appengine.ext import ndb
from google.appengine.api import search
from Handlers.BaseHandler import *
import logging

class ResModel(ndb.Model):
    user = ndb.KeyProperty(required=True)
    driver = ndb.KeyProperty()
    email = ndb.StringProperty()
    capacity = ndb.IntegerProperty(default=0) # seat (0), trunk (1), big (2),    
    details = ndb.StringProperty() 
    delivstart = ndb.DateProperty(required=True)
    delivend = ndb.DateProperty(required=True)    
    pickup = ndb.BooleanProperty(default=False)     # sender picks up shit at dest
    dropoff = ndb.BooleanProperty(default=True)     # sender drops off shit at start
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location 
    rates = ndb.IntegerProperty()   # Offer price
    ratestemp = ndb.IntegerProperty()   # Get rid of this later
    created = ndb.DateTimeProperty(auto_now_add=True)    

    def driver_name(self):
        return self.driver.get().first_name      
    
    def to_dict(cls):
        route = {
            'delivby' : cls.delivend.strftime('%m/%d/%Y'),
            'receiver' : cls.driver_name(),
            'price' : cls.rates,
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'confirmed' : True,
            'pickup' : cls.pickup,
            'dropoff' : cls.dropoff
        }
        return route