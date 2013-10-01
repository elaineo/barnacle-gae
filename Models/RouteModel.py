from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Models.ReservationModel import *
from Utils.RouteUtils import *
from Utils.Defs import miles2m

class RepeatRoute(ndb.Model):
    period = ndb.IntegerProperty() # weekly (0), or monthly (1)
    dayweek = ndb.IntegerProperty(repeated=True) # day of week, Sunday(0) to Sat(6) 
    weekmonth = ndb.IntegerProperty(repeated=True) # week of month1-4

class Route(ndb.Model):
    userkey = ndb.KeyProperty(required=True)  # the user_pref it is connected to
    capacity = ndb.IntegerProperty(default=0) # car (0), SUV (1), flatbed (2), hauler (3)
    details = ndb.TextProperty() # text describing
    roundtrip = ndb.BooleanProperty(default=False)
    repeatr = ndb.StructuredProperty(RepeatRoute)
    created = ndb.DateTimeProperty(auto_now_add=True)
    delivstart = ndb.DateProperty(required=True)
    delivend = ndb.DateProperty(required=True)
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    locstart = ndb.StringProperty(required=True) #text descr of location
    locend = ndb.StringProperty(required=True) #text descr of location
    pathpts = ndb.GeoPtProperty(repeated=True)     

    def _pre_put_hook(self):
        p = RouteUtils().setloc(self, self.locstart, self.locend)        
        if p:
            self = p
        else:
            raise Exception('error')
            
    def suggest_rate(self):
        """ I don't really know """
        d = 100
        if self.capacity < 4:
            sugg = (d/miles2m)*(self.capacity+2)*0.05
        else:
            if d < miles2m*20:
                sugg = (d/miles2m)*0.5
            else:
                sugg = (d/miles2m)*0.05
        return "%.2f" % sugg
    
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
        return UserPrefs.by_userid(self.userid).first_name
        
    def prof_url(self):
        return userkey.get().profile_url()

    def reserve_url(self):
        """ url for making reservation """
        return '/reserve/route/' + self.key.urlsafe()
    
    def num_requests(self):
        r = Reservation.by_route(self.key)
        return r.count()        
        
    def num_confirmed(self):
        r = Reservation.route_confirmed(self.key)
        return r 
    
    def to_dict(cls):
        route = {
            'post_url' : cls.post_url(),
            'delivstart' : cls.delivstart.strftime('%m/%d/%Y'),
            'delivend' : cls.delivend.strftime('%m/%d/%Y'),
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'num_requests': cls.num_requests()
        }
        return route
    
    def gen_repeat(self):
        r = {}
        r['repeat'] = False
        if self.repeatr:
            weekdays = ['Sunday','Monday','Tuesday','Wednesday','Thursday',
            'Friday','Saturday']
            rstring = 'Every '
            if self.repeatr.dayweek == None:
                return r
            if self.repeatr.period == 1:
                weekmonths = ['1st', '2nd', '3rd', '4th']
                mstring = ''
                for m in self.repeatr.weekmonth:
                    mstring = mstring + ' and ' + weekmonths[m]
                rstring = rstring + mstring[5:] + ' '
            for w in self.repeatr.dayweek:
                rstring = rstring + weekdays[w] + ', '
            rstring = rstring + 'until ' + self.delivend.strftime('%m/%d/%Y')
            r['repeat'] = True
            r['repeatr'] = self.repeatr.to_dict()
            r['rstring'] = rstring
        return r

        
    @classmethod
    def by_userkey(cls,userkey):
        return cls.query().filter(cls.userkey==userkey)
    @classmethod
    def get_all(cls):
        return cls.query()
    
    def __eq__(self, other):
        return self.userid==other.userid and self.created==other.created
        
    @classmethod
    def dist_fetch(cls,max_miles,start,dest,bbstart,bbdest):
        #this doesn't work because FU google
        max_distance=max_miles*miles2m
        q = cls.query().filter(ndb.AND(cls.start.lat<bbstart['maxLat'], 
                cls.start.lat>bbstart['minLat'], cls.start.lon<bbstart['maxLon'], 
                cls.start.lon>bbstart['minLon'], cls.dest.lat<bbdest['maxLat'], 
                cls.dest.lat>bbdest['minLat'], cls.dest.lon<bbdest['maxLon'], 
                cls.dest.lon>bbdest['minLon']))
        return q
        
        
class ExpiredRoute(ndb.Model):
    userkey = ndb.KeyProperty()  # the user_pref it is connected to
    capacity = ndb.IntegerProperty() # car (0), SUV (1), flatbed (2), hauler (3)
    details = ndb.TextProperty() # text describing
    repeatr = ndb.StructuredProperty(RepeatRoute)
    delivstart = ndb.DateProperty()
    delivend = ndb.DateProperty()
    start = ndb.GeoPtProperty()
    dest = ndb.GeoPtProperty()
    
    def to_dict(cls):
        route = {
            'userkey': cls.userkey.urlsafe(),
            'capacity' : cls.capacity,
            'details' : cls.details,
            'delivstart' : cls.delivstart.strftime('%m/%d/%Y'),
            'delivend' : cls.delivend.strftime('%m/%d/%Y'),
            'start' : {cls.start.lat, cls.start.lon},
            'dest' : {cls.dest.lat, cls.dest.lon}
        }
        return route
    