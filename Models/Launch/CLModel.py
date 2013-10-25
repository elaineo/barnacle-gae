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
    delivend = ndb.DateProperty(required=True)
    start = ndb.GeoPtProperty()
    dest = ndb.GeoPtProperty()
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location
    pathpts = ndb.GeoPtProperty(repeated=True)        

    def _pre_put_hook(self):
        p = RouteUtils().setloc(self, self.locstart, self.locend)        
        if p:
            self = p
        else:
            raise Exception('error')                
    
    def post_url(self):
        """ url for public view of post """
        return '/scraped/' + self.key.urlsafe()
        
    
    def to_dict(cls):
        route = {  
            'routekey' : cls.key.urlsafe(),
            'post_url' : cls.post_url(),
            'post_date' : cls.posted.strftime('%m/%d/%Y'),
            'delivend' : cls.delivend.strftime('%m/%d/%Y'),
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'details' : cls.details.replace('\\n','<br>'),
            'cl_url' :cls.clurl,
            'email' : cls.email
        }
        return route
    
class ZimModel(ndb.Model):
    fbid = ndb.StringProperty() # fb unique identifier
    clurl = ndb.StringProperty()
    details = ndb.TextProperty() # text describing
    delivend = ndb.DateProperty(required=True)
    start = ndb.GeoPtProperty()
    dest = ndb.GeoPtProperty()
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location
    pathpts = ndb.GeoPtProperty(repeated=True)        
    distance = ndb.IntegerProperty()
    creation_date = ndb.DateTimeProperty(auto_now_add=True)    
    

    def _pre_put_hook(self):
        p, d = RouteUtils().setloc(self, self.locstart, self.locend)        
        if p:
            self = p
            self.distance = d
        else:
            raise Exception('error')                
    
    def post_url(self):
        """ url for public view of post """
        return '/scraped/' + self.key.urlsafe()
        
    
    def to_dict(cls):
        route = {  
            'fbid' : cls.fbid,
            'routekey' : cls.key.urlsafe(),
            'delivend' : cls.delivend.strftime('%m/%d/%Y'),
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'details' : cls.details.replace('\\n','<br>'),
            'cl_url' :cls.clurl
        }
        if cls.creation_date:
            route['post_date'] = cls.creation_date.strftime('%m/%d/%Y')
        return route    
        
    def profile_image_url(self, mode = None):
        """ Retrieve link to profile thumbnail or default """
        # use FB picture
        fburl = 'http://graph.facebook.com/'+self.fbid+'/picture?redirect=false'
        if mode == 'small':
            fburl += '&width=100&height=100'
        else:
            fburl += '&width=720&height=720'
        try:
            fbdata = json.loads(urllib2.urlopen(fburl).read())
            if fbdata['data']:
                return fbdata['data']['url']
        except:
            logging.error('FB server shat the bed')