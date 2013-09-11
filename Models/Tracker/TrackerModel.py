from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Utils.RouteUtils import *
import logging

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
    status = ndb.IntegerProperty(default=0)  #0 inactive, 1 active, 2 waiting

    def post_url(self):
        """ url for public view of post """
        return '/track/view/' + self.key.urlsafe()
            
    def to_dict(cls):
        route = {  
            'routekey' : cls.key.urlsafe(),
            'post_url' : cls.post_url(),
            'locstart' : cls.locstart,
            'locend' : cls.locend,
            'delivend' : cls.delivend.strftime('%m/%d/%Y'),
            'statusint' : cls.status
        }
        if cls.points:
            route['last_seen'] = cls.points[-1].created.strftime('%m/%d/%Y %H:%M')
            route['disppoints'] = True
            points = []
            for px in cls.points:
                p = { 'lat': "%.2f" % px.loc.lat,
                      'lon': "%.2f" % px.loc.lon,
                      'locstr' : px.locstr,
                      'time' : px.created.strftime('%m/%d/%Y %H:%M'),
                      'msg' : px.msg }
                points.append(p)
            route['points'] = points
        else:
            route['last_seen'] = ''
            route['disppoints'] = False
        if cls.status==1:
            route['status'] = 'active'
        elif cls.status==2:
            route['status'] = 'waiting'
        else:
            route['status'] = 'inactive'
        return route
    
    @classmethod
    def by_driver(cls,userkey):
        return cls.query().filter(cls.driver==userkey)  #add filter for status    