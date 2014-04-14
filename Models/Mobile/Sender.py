from google.appengine.ext import ndb
import logging
import uuid
import json
import urllib2


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

