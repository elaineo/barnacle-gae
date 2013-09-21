from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Utils.RouteUtils import *
import logging
from datetime import *

class TrackPt(ndb.Model):   
    loc = ndb.GeoPtProperty()
    locstr = ndb.StringProperty()
    created = ndb.DateTimeProperty()
    speed = ndb.FloatProperty()
    msg = ndb.StringProperty()

class TrackerModel(ndb.Model):
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
            route['last_seen'] = cls.points[-1].created.strftime('%m/%d/%Y %H:%M')
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
        if cls.status==0:
            route['status'] = 'Active'
        elif cls.status==2:
            route['status'] = 'Awaiting Confirmation'
        elif cls.status==99:
            route['status'] = 'Completed and Confirmed'
        else:
            route['status'] = 'Inactive'
        return route
    
    @classmethod
    def by_driver(cls,userkey,status=None):
        if status is not None:
            return cls.query(ndb.AND(cls.driver==userkey, cls.status==status)) 
        else:
            return cls.query().filter(cls.driver==userkey)  
        
    def tzdelta(self):
        return timedelta(0,self.tzoffset)