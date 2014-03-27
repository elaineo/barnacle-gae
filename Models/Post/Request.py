from google.appengine.ext import ndb
from Models.Post.Post import Post
from Models.ImageModel import *
from Utils.data.Defs import miles2m
from Utils.RouteUtils import roundPoint
import logging

#use this for status, PostStatus for dead
RequestStatus = ['INCOMP', 'IGNORE', 'NO_CC', 'WATCH', 'PURSUE', 'PRIORITY']

class ReqStats(ndb.Model):
    """ Other stats we want: 
      if they cancel after seeing suggested price
      low/high end UPS, if they accept"""
    sugg_price = ndb.IntegerProperty()
    seed = ndb.IntegerProperty()
    distance = ndb.IntegerProperty()
    views = ndb.IntegerProperty(default=0)
    notes = ndb.TextProperty(default='')
    status = ndb.IntegerProperty(default=RequestStatus.index('INCOMP'))

class Request(Post):
    category = ndb.IntegerProperty(default=0) # car (0), SUV (1), flatbed (2)
    rates = ndb.IntegerProperty()       # if defined, accept any offers <=
    delivby = ndb.DateProperty(required=True)
    stats = ndb.StructuredProperty(ReqStats)
    img_id = ndb.IntegerProperty()     
    
    def has_cc(self):
        # Does this sender have an associated cc#?
        u = self.key.parent().get()
        return u.cc    

    def post_url(self):
        """ url for public view of post """
        return '/request/' + self.key.urlsafe()

    def edit_url(self):
        """ url for editing post"""
        return '/request/edit/' + self.key.urlsafe()

    def delete_url(self):
        """ url for deleting post"""
        return '/request/delete/' + self.key.urlsafe()    

    def repost_url(self):
        """ url for reposting """
        return '/request/repost/' + self.key.urlsafe()        
    
    def increment_views(self):
        if self.stats:
            self.stats.views = self.stats.views+1
            self.put()
        
    def to_dict(cls,incl_user=False):
        route = cls.base_dict(incl_user)
        route['delivby'] = cls.delivby.strftime('%m/%d/%Y')
        route['rates'] = cls.rates
        route['category'] = cls.category
        route['img_url'] = cls.image_url()
        route['img_thumb'] = cls.image_url('small')
        route['edit_url'] = cls.edit_url()
        route['delete_url'] = cls.delete_url()
        route['post_url'] = cls.post_url()
        if cls.has_cc():
            route['valid'] = True
        else:
            route['valid'] = False 
        return route
        
    def to_search(cls):
        u = cls.key.parent().get()
        route = {
            'edit_url' : cls.edit_url(),
            'delete_url':cls.delete_url(),
            'post_url' : cls.post_url(),
            'routekey' : cls.key.urlsafe(),
            'delivby' : cls.delivby.strftime('%b-%d-%y'),
            'start' : cls.locstart,
            'dest' : cls.locend,
            'thumb_url': u.profile_image_url('small'),
            'first_name' : u.first_name,
            'fbid' : u.userid
        }
        if cls.details:
            route['desc'] = cls.details[:200] + '...'
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
                        
    ### Search utils ::...........................::::::::::::::::::::::
    @classmethod
    def search_route(cls, path, delivstart, delivend, precision):
        results = []
        qall = cls.query(cls.delivby >= delivstart, cls.dead==0)
        for q in qall:                    
            # Make sure it's not garbage
            if q.stats.status > RequestStatus.index('IGNORE'):
                start = roundPoint(q.start, precision)
                dest = roundPoint(q.dest, precision)
                pathpts = [roundPoint(pp, precision) for pp in path]   
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
        
    def params_fill(self):
        params = {}
        params['delivby'] = self.delivby.strftime('%m/%d/%Y')
        params['locstart'] = self.locstart
        params['locend'] = self.locend
        return params