from google.appengine.ext import ndb
from google.appengine.api import search
from Handlers.BaseHandler import *
from Utils.Defs import miles2m
import logging

class Request(ndb.Model):
    userkey = ndb.KeyProperty(required=True)  # the user_pref it is connected to
    capacity = ndb.IntegerProperty(default=0) # car (0), SUV (1), flatbed (2)
    rates = ndb.IntegerProperty()
    items = ndb.TextProperty() 
    created = ndb.DateTimeProperty(auto_now_add=True)
    delivby = ndb.DateProperty(required=True)
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location    
    
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
    def num_offers(self):
        r = DeliveryOffer.by_route(self.key)
        return r.count()    

    def num_confirmed(self):
        r = DeliveryOffer.route_confirmed(self.key)
        return r 
            
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
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'rates' : cls.rates,
            'capacity' : cls.capacity,
            'reqitems' : cls.items,
            'num_offers' : cls.num_offers()
        }
        if incl_user:
            u = cls.userkey.get()
            udict = {
                'prof_img' : u.profile_image_url('small'),
                'first_name' : u.nickname()
            }
            route.update(udict)
        return route
        
    def __eq__(self, other):
        return self.userid==other.userid and self.created==other.created
       
#save what they searched
class SearchEntry(ndb.Model):
    remoteip = ndb.StringProperty(required=True) #don't know who they are, don't care
    created = ndb.DateTimeProperty(auto_now_add=True)
    delivby = ndb.DateProperty(required=True)
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location   

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
    
    def to_dict(cls):
        route = {
            'userkey': cls.userkey.urlsafe(),
            'rates': cls.rates,
            'items' : cls.items,
            'delivby' : cls.delivby.strftime('%m/%d/%Y'),
            'start' : {cls.start.lat, cls.start.lon},
            'dest' : {cls.dest.lat, cls.dest.lon}
        }
        return route
