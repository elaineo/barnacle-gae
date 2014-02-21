from google.appengine.ext import ndb
from Models.User.Account import *

""" Base class for Routes and Requests """
""" Parent will be a user """
PostStatus = ['ALIVE', 'EXPIRED', 'DELETED', 'DONE', 'DECLINED', 'FLAGGED']    
    
class Post(ndb.Model):
    capacity = ndb.IntegerProperty(default=0) # car (0), SUV (1), flatbed (2), hauler (3) carryon (-1)
    details = ndb.TextProperty() # text describing
    created = ndb.DateTimeProperty(auto_now_add=True)
    start = ndb.GeoPtProperty()
    dest = ndb.GeoPtProperty()
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location
    matches = ndb.KeyProperty(repeated=True)  #store keys of matches
    offers = ndb.KeyProperty(repeated=True)  #store keys of offers
    dead = ndb.IntegerProperty(default=0)    # see PostStatus   
    
    def post_url(self):
        """ url for public view of post """
        return '/post/' + self.key.urlsafe()

    def edit_url(self):
        """ url for editing post"""
        return '/post/edit/' + self.key.urlsafe()

    def delete_url(self):
        """ url for deleting post"""
        return '/post/delete/' + self.key.urlsafe()
        
    def first_name(self):
        return self.key.parent().get().first_name
        
    def prof_url(self):
        return self.key.parent().get().profile_url()

    def reserve_url(self):
        """ url for making reservation """
        return '/reserve/route/' + self.key.urlsafe()
    
    def message_url(self):        
        return '/message/route/' + self.key.urlsafe()        
    
    def num_offers(self):
        q=0
        for r in self.offers:
            try:
                rr = r.get()
                if rr.dead==0:
                    q=q+1
            except:
                continue
        return q    
        
    def num_matches(self):
        q=0
        for r in self.matches:
            try:
                rr = r.get()
                if rr.dead==0:
                    q=q+1
            except:
                continue
        return q        
        
    def num_confirmed(self):
        q=0
        for r in self.offers:
            try:
                rr = r.get()
                if rr.confirmed:
                    q=q+1
            except:
                continue
        return q
    
    def base_dict(cls, incl_user=False):
        route = {
            'routekey' : cls.key.urlsafe(),
            'reserve_url' : cls.reserve_url(),
            'edit_url' : cls.edit_url(),
            'delete_url':cls.delete_url(),
            'post_url' : cls.post_url(),
            'message_url' : cls.message_url(),
            'capacity' : cls.capacity,
            'created' : cls.created.strftime('%m/%d/%Y'),
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'details' : cls.details,
            'num_confirmed' : cls.num_confirmed(), 
            'num_offers': cls.num_offers(),
            'num_matches' : cls.num_matches()
        }
        if incl_user:
            u = cls.key.parent().get()
            route.update(u.params_fill_sm())
        return route    
            
    @classmethod
    def by_userkey(cls,userkey, dead=0):
        return cls.query(cls.dead==dead, ancestor=userkey)
    @classmethod
    def by_match(cls,key, dead=0):
        return cls.query(cls.matches==key, cls.dead==dead)
    
    def __eq__(self, other):
        return self.userid==other.userid and self.created==other.created        