from google.appengine.ext import ndb
from google.appengine.api import search
from Handlers.BaseHandler import *
import logging

"""Anonymous Reservation"""

class Reservation(ndb.Model):
    email = ndb.StringProperty()
    capacity = ndb.IntegerProperty(default=0) # seat (0), trunk (1), big (2),    
    details = ndb.TextProperty() 
    delivstart = ndb.DateProperty()
    delivby = ndb.DateProperty()
    start = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    dest = ndb.GeoPtProperty()
    locend = ndb.StringProperty(required=True) #text descr of location
    rates = ndb.IntegerProperty()   # Offer price
    created = ndb.DateTimeProperty(auto_now_add=True)    

    
    def to_dict(cls):
        route = {
            'rates' : cls.rates,
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'delivby' : cls.delivby.strftime('%m/%d/%Y')
        }
        if cls.delivstart:
            route['delivstart'] = cls.delivstart.strftime('%m/%d/%Y')
        return route