from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Models.ReservationModel import *
from Utils.RouteUtils import *
import logging

class CLModel(ndb.Model):
    email = ndb.StringProperty() # email address
    clurl = ndb.StringProperty()
    details = ndb.TextProperty() # text describing
    posted = ndb.DateTimeProperty(required=True)
    delivby = ndb.DateProperty(required=True)
    start = ndb.GeoPtProperty()
    dest = ndb.GeoPtProperty()
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location

    def post_url(self):
        """ url for public view of post """
        return '/scraped/' + self.key.urlsafe()
        
    
    def to_dict(cls):
        route = {  
            'routekey' : cls.key.urlsafe(),
            'post_url' : cls.post_url(),
            'post_date' : cls.posted.strftime('%m/%d/%Y'),
            'delivend' : cls.delivby.strftime('%m/%d/%Y'),
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'details' : cls.details.replace('\\n','<br>'),
            'cl_url' :cls.clurl,
            'email' : cls.email
        }
        return route
    