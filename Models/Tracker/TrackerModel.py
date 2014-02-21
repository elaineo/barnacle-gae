from google.appengine.ext import ndb
from Handlers.BaseHandler import *
import logging
from datetime import *

class TrackPt(ndb.Model):   
    loc = ndb.GeoPtProperty()
    locstr = ndb.StringProperty()
    created = ndb.DateTimeProperty()
    speed = ndb.FloatProperty()
    msg = ndb.StringProperty()

class TrackerModel(ndb.Model):
    reservation = ndb.KeyProperty()   #attach this thing to a reservation 
    sender = ndb.KeyProperty()      #attach to a sender
    driver = ndb.KeyProperty(required=True)
    points = ndb.StructuredProperty(TrackPt, repeated=True)
    start = ndb.GeoPtProperty(required=True)
    dest = ndb.GeoPtProperty(required=True)
    delivend = ndb.DateProperty()    
    locstart = ndb.StringProperty() #text descr of location
    locend = ndb.StringProperty() #text descr of location
    tzoffset = ndb.IntegerProperty()
    status = ndb.IntegerProperty(default=1)  #1 inactive, 0 active, 2 waiting, 99 done

    def post_url(self):
        """ url for public view of post """
        return '/track/view/' + self.key.urlsafe()
        
    def mobile_url(self):
        """ url for mobile view of post """
        return '/track/mobile/' + self.key.urlsafe()        
            
    def to_dict(cls,abbrev=False):
        route = {  
            'routekey' : cls.key.urlsafe(),
            'post_url' : cls.post_url(),
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'delivend' : cls.delivend.strftime('%m/%d/%Y'),
            'statusint' : cls.status
        }
        if abbrev:
            return route
        if cls.points:
            route['last_seen'] = (cls.points[-1].created + cls.tzdelta()).strftime('%m/%d/%Y %H:%M')
            route['disppoints'] = True
            points = []
            for px in cls.points:
                p = { 'lat': "%.2f" % px.loc.lat,
                      'lon': "%.2f" % px.loc.lon,
                      'locstr' : px.locstr,
                      'time' : (px.created + cls.tzdelta()).strftime('%m/%d/%Y %H:%M'),
                      'msg' : px.msg }
                points.insert(0,p)
            route['points'] = points
        else:
            route['last_seen'] = ''
            route['disppoints'] = False
        route['dispeta'] = False
        if cls.status==0:
            route['status'] = 'Active'            
            if cls.points:
                route['dispeta'] = True
                route['lastpt'] = str(cls.points[-1].loc.lat) + ',' + str(cls.points[-1].loc.lon)
                route['destpt'] = str(cls.dest.lat) + ',' + str(cls.dest.lon)
        elif cls.status==2:
            route['status'] = 'Awaiting Confirmation'
        elif cls.status==99:
            route['status'] = 'Completed and Confirmed'
        else:
            route['status'] = 'Inactive'
        return route
    
    @classmethod
    def by_driver(cls,userkey,status=None,comp=False):
        if status is not None:
            return cls.query(ndb.AND(cls.driver==userkey, cls.status==status))
        elif comp:
            return cls.query(cls.status!=99).filter(cls.driver==userkey)
        else:
            return cls.query().filter(cls.driver==userkey)  

    @classmethod
    def by_reservation(cls,rezkey):
        return cls.query().filter(cls.reservation==rezkey)  
    @classmethod
    def by_sender(cls,key):
        return cls.query().filter(cls.sender==key)
            
    def tzdelta(self):
        return timedelta(0,self.tzoffset)