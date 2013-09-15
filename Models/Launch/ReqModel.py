from google.appengine.ext import ndb
from google.appengine.api import search
from Handlers.BaseHandler import *
import logging

class ReqModel(ndb.Model):
    user = ndb.KeyProperty(required=True)
    email = ndb.StringProperty()
    capacity = ndb.IntegerProperty(default=0) # car (0), SUV (1), flatbed (2),    
    details = ndb.TextProperty() 
    created = ndb.DateTimeProperty(auto_now_add=True)
    delivstart = ndb.DateProperty(required=True)
    delivend = ndb.DateProperty(required=True)    
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location    
   
