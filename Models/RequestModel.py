from google.appengine.ext import ndb
from google.appengine.api import search
from Handlers.BaseHandler import *
from Utils.Defs import miles2m
from Utils.RouteUtils import roundPoint
import logging

RequestStatus = ['IGNORE', 'WATCH', 'PURSUE', 'PRIORITY']

class ReqStats(ndb.Model):
    """ Other stats we want: 
      if they cancel after seeing suggested price
      low/high end UPS, if they accept"""
    sugg_price = ndb.IntegerProperty()
    seed = ndb.IntegerProperty()
    distance = ndb.IntegerProperty()
    views = ndb.IntegerProperty(default=0)
    notes = ndb.TextProperty(default='')
    status = ndb.IntegerProperty(default=RequestStatus.index('PURSUE'))

class Request(ndb.Model):
    userkey = ndb.KeyProperty(required=True)  # the user_pref it is connected to
    capacity = ndb.IntegerProperty(default=0) # car (0), SUV (1), flatbed (2)
    category = ndb.IntegerProperty(default=0) # car (0), SUV (1), flatbed (2)
    rates = ndb.IntegerProperty()
    items = ndb.TextProperty(default='') 
    created = ndb.DateTimeProperty(auto_now_add=True)
    delivby = ndb.DateProperty(required=True)
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location    
    matches = ndb.KeyProperty(repeated=True)  #store keys of matches    
    stats = ndb.StructuredProperty(ReqStats)
    img_id = ndb.IntegerProperty()     
    
    def post_url(self):
        """ url for public view of post """
        return '/post/' + self.key.urlsafe()

    def edit_url(self):
        """ url for editing post"""
        return '/post/edit/' + self.key.urlsafe()

    def delete_url(self):
        """ url for deleting post"""
        return '/post/delete/' + self.key.urlsafe()
        
    def prof_url(self):
        return userkey.get().profile_url()

    def reserve_url(self):
        """ url for making reservation """
        return '/reserve/route/' + self.key.urlsafe()
    def message_url(self):        
        return '/message/route/' + self.key.urlsafe()                
        
    def num_offers(self):
        r = DeliveryOffer.by_route(self.key)
        return r.count()    

    def num_confirmed(self):
        r = DeliveryOffer.route_confirmed(self.key)
        return r 
    
    def increment_views(self):
        if self.stats:
            self.stats.views = self.stats.views+1
            self.put()

    @classmethod
    def by_match(cls,key):
        return cls.query().filter(cls.matches==key)            
    @classmethod
    def by_userkey(cls,userkey):
        return cls.query().filter(cls.userkey==userkey)
    @classmethod
    def get_all(cls):
        return cls.query()

    @classmethod
    def newest(cls,num):
        return cls.query().order(-cls.created).fetch(num)
        
    def to_dict(cls,incl_user=False):
        route = {
            'post_url' : cls.post_url(),
            'delivby' : cls.delivby.strftime('%m/%d/%Y'),
            'created' : cls.created.strftime('%m/%d/%Y'),
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'rates' : cls.rates,
            'capacity' : cls.capacity,
            'category' : cls.category,
            'items' : cls.items,
            'num_offers' : cls.num_offers(),
            'num_matches' : len(cls.matches),
            'image_url' : cls.image_url()
        }
        if incl_user:
            u = cls.userkey.get()
            udict = {
                'prof_img' : u.profile_image_url('small'),
                'first_name' : u.nickname()
            }
            route.update(udict)
        return route
        
    def to_search(cls):
        u = cls.userkey.get()
        route = {
            'routekey' : cls.key.urlsafe(),
            'delivby' : cls.delivby.strftime('%b-%d-%y'),
            'start' : cls.locstart,
            'dest' : cls.locend,
            'desc' : cls.items[:200],
            'thumb_url': u.profile_image_url('small'),
            'first_name' : u.first_name,
            'fbid' : u.userid
        }
        return route        

    def image_url(self, mode = 'original'):
        """ Retrieve link to profile thumbnail or default """
        if self.img_id:
            profile_image = ImageStore.get_by_id(self.img_id)
            if profile_image:
                buf = '/img/' + str(self.img_id) + '?key=' + profile_image.fakehash
                if mode:
                    buf += '&mode=' + mode
                return buf
        return '/static/img/icons/nophoto1.png'
        
        
    def __eq__(self, other):
        return self.userid==other.userid and self.created==other.created
        
    ### Search utils ::...........................::::::::::::::::::::::
    @classmethod
    def search_route(cls, pathpts, delivstart, delivend, precision):
        results = []
        qall = cls.query().filter(cls.delivby >= delivstart)
        for q in qall:                    
            start = roundPoint(q.start, precision)
            dest = roundPoint(q.dest, precision)
            if start in pathpts and dest in pathpts:
                # Make sure it's going the right way
                if pathpts.index(start) <= pathpts.index(dest):
                    results.append(q)
        return results
       
#save what they searched
class SearchEntry(ndb.Model):
    remoteip = ndb.StringProperty(required=True) #don't know who they are, don't care
    created = ndb.DateTimeProperty(auto_now_add=True)
    delivby = ndb.DateProperty()
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    dist = ndb.FloatProperty(default=100.0)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location   
    # matches = ndb.KeyProperty(repeated=True)
    
    @classmethod
    def by_ip(cls,remoteip):
        return cls.query().filter(cls.remoteip==remoteip).order(-cls.created).get()
        
    def params_fill(self, params):
        params['delivby'] = self.delivby.strftime('%m/%d/%Y')
        params['locstart'] = self.locstart
        params['locend'] = self.locend
        return params
    
class ExpiredRequest(ndb.Model):
    userkey = ndb.KeyProperty()  # the user_pref it is connected to
    rates = ndb.IntegerProperty()
    items = ndb.TextProperty() 
    delivby = ndb.DateProperty()
    start = ndb.GeoPtProperty()
    dest = ndb.GeoPtProperty()
    locstart = ndb.StringProperty() #text descr of location
    locend = ndb.StringProperty() #text descr of location    
    oldkey = ndb.KeyProperty()
    img_id = ndb.IntegerProperty()     
    stats = ndb.StructuredProperty(ReqStats)
    
    def to_dict(cls):
        route = {
            'name': cls.userkey.get().first_name,
            'userkey': cls.userkey.urlsafe(),
            'rates': cls.rates,
            'items' : cls.items,
            'delivby' : cls.delivby.strftime('%m/%d/%Y'),
            'start' : cls.locstart,
            'dest' : cls.locend,
            'start' : {cls.start.lat, cls.start.lon},
            'dest' : {cls.dest.lat, cls.dest.lon},
            'img_url' : cls.image_url(),
            'routekey' : cls.key.urlsafe()
        }
        return route
    
    def image_url(self, mode = 'original'):
        """ Retrieve link to profile thumbnail or default """
        if self.img_id:
            profile_image = ImageStore.get_by_id(self.img_id)
            if profile_image:
                buf = '/img/' + str(self.img_id) + '?key=' + profile_image.fakehash
                if mode:
                    buf += '&mode=' + mode
                return buf
        return '/static/img/barnacle.png'    
    
    @classmethod
    def by_key(cls,key):
        return cls.query().filter(cls.oldkey==key).get()
