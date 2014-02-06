from google.appengine.ext import ndb
from Handlers.BaseHandler import *
import logging
from datetime import *

class Transaction(ndb.Model):
    reservation = ndb.KeyProperty()   #attach this thing to a reservation 
    sender = ndb.KeyProperty(required=True)      #attach to a sender
    driver = ndb.KeyProperty(required=True)
    delivered = ndb.BooleanProperty(default=False)
    paid = ndb.BooleanProperty(default=False)
    delivend = ndb.DateProperty() 
    created = ndb.DateTimeProperty(auto_now_add=True)
            
    @classmethod
    def by_driver(cls,userkey,status=None,comp=False):
        if status is not None:
            return cls.query(ndb.AND(cls.driver==userkey, cls.status==status))
        elif comp:
            return cls.query(cls.status!=99).filter(cls.driver==userkey)
        else:
            return cls.query().filter(cls.driver==userkey)  

    @classmethod
    def by_reservation(cls,rezkey):
        return cls.query().filter(cls.reservation==rezkey)  
    @classmethod
    def by_sender(cls,key):
        return cls.query().filter(cls.sender==key)