from google.appengine.ext import ndb
from Handlers.BaseHandler import *
import logging
from datetime import *

class Transaction(ndb.Model):
    reservation = ndb.KeyProperty()   #attach this thing to a reservation 
    route = ndb.KeyProperty()       #attach this thing to a route
    sender = ndb.KeyProperty(required=True)      #attach to a sender
    driver = ndb.KeyProperty(required=True)
    delivered = ndb.BooleanProperty(default=False)
    payout = ndb.FloatProperty(default=0.00)
    paid = ndb.BooleanProperty(default=False)
    delivend = ndb.DateProperty() 
    created = ndb.DateTimeProperty(auto_now_add=True)
            
    @classmethod
    def by_driver(cls,driver,paid=None):
        if paid is not None:
            return cls.query(ndb.AND(cls.driver==driver, cls.paid==paid))
        else:
            return cls.query().filter(cls.driver==driver)  

    @classmethod
    def by_reservation(cls,rezkey):
        return cls.query().filter(cls.reservation==rezkey)  
    @classmethod
    def by_sender(cls,key):
        return cls.query().filter(cls.sender==key)
        
    @classmethod
    def earnings_by_userkey(cls, key):
        trans = cls.query().filter(cls.driver == key)
        total = 0.00
        for t in trans:
            total = total + t.payout
        return total
        
    def to_dict(cls):
        route = ExpiredRoute.by_key(cls.route)
        r = { 'sender': cls.sender.get().fullname,
              'locstart' : route.locstart,
              'locend' : route.locend,
              'delivend' : cls.delivend.strftime('%m/%d/%Y'),
              'earnings' : cls.payout }
        return r