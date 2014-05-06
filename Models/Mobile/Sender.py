from google.appengine.ext import ndb
import logging
import json

class MobileStats(ndb.Model):
    """ I'm not sure what we're gonna do here yet """
    referral = ndb.StringProperty()
    
class Address(ndb.Model):
    name = ndb.StringProperty() #recipient's name
    street = ndb.StringProperty() #street address
    apt = ndb.StringProperty() 
    city = ndb.StringProperty() 
    state = ndb.StringProperty() 
    zip = ndb.StringProperty() 
    locpt = ndb.GeoPtProperty()
    type = ndb.IntegerProperty(default=0) #0 for origin, 1 for dest
    
    @classmethod
    def by_userkey(cls, key):
        u = cls.query(ancestor=key)
        return u   
        
    @classmethod
    def by_userkey_type(cls, key, type):
        u = cls.query(ancestor=key,type=type)
        return u   
        
    def to_dict(cls):
        address = {
            'addrkey' : cls.key.urlsafe(),
            'name' : cls.name,
            'street' : cls.street
        }
        return address
