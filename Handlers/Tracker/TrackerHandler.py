import logging
import json
from datetime import *
from google.appengine.ext import ndb
from datetime import *

from Handlers.BaseHandler import *
from Models.Tracker.TrackerModel import *
from Utils.ValidUtils import parse_date

class TrackerHandler(BaseHandler):
    def get(self, action=None, key=None):
        if action=='updateloc':
            self.__debugcheckin()  
        elif action=='create':
            self.__debug()     
        elif action=='getroutes':
            self.__getroutes()
        elif action=='jsonroute' and key:
            try:
                route=ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return  
            rdump = RouteUtils().dumptrack(route, [route.start,route.dest])
            self.response.headers['Content-Type'] = "application/json"
            self.write(rdump)
        elif action=='view' and key:
            self.__view_page(key,False)
        elif action=='mobile' and key:
            self.__view_page(key,True)            
            
    def post(self, action=None):       
        if not self.user_prefs:
            logging.error('Not logged in')
            response = { 'status': 'fail'}            
            self.response.headers['Content-Type'] = "application/json"
            self.write(response)
            return
        if action=='updateloc':
            self.__updateloc()
        elif action=='create':
            self.__create()
        else:
            return
                    
    def __updateloc(self):
        #trackermodel
        data = json.loads(self.request.body)
        logging.info(data)
        try:
            lat = float(data['lat'])
            lon = float(data['lon'])
            # todo: add speed
            loc =  ndb.GeoPt(lat=lat,lon=lon)  
            response = { 'status': 'ok'}
        except:
            response = { 'status': 'fail'}
        try:
            locstr = data['locstr']
            msg = data['msg']
        except:
            locstr = ''           
            msg = ''
        if loc:
            point = TrackPt(loc=loc, created=datetime.now(), locstr=locstr, msg=msg)
            routes = TrackerModel.by_driver(self.user_prefs.key)
            for r in routes:
                r.points.append(point)
                r.put()
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))              
        
    def __view_page(self,key,mobile=False):
        try:
            p = ndb.Key(urlsafe=key).get()
            self.params.update(p.to_dict())
            if mobile:
                self.render('mobile/track.html', **self.params)
            else:
                self.render('track/track.html', **self.params)
            return
        except:
            self.abort(409)
            return         
            
    def __create(self):
        data = json.loads(self.request.body)
        logging.info(data)    
        try:
            startlat = float(data['startlat'])
            startlon = float(data['startlon'])
            destlat = float(data['destlat'])
            destlon = float(data['destlon'])
            locstart = data['locstart']
            locend = data['locend']
            delivend = parse_date(data['delivend'])
            start = ndb.GeoPt(lat=startlat, lon=startlon)
            dest = ndb.GeoPt(lat=destlat, lon=destlon)
            response = { 'status': 'ok'}
        except:
            response = { 'status': 'fail'}            
        if start and dest:
            track = TrackerModel(driver = self.user_prefs.key, start = start, 
                dest=dest, delivend=delivend, locstart=locstart, locend=locend)
            track.put()
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))              

    def __getroutes(self):
        if not self.user_prefs.key:
            response = { 'status': 'fail'}            
        else:
            routes=[]
            tracks = TrackerModel.by_driver(self.user_prefs.key)
            for t in tracks:
                routes.append(t.to_dict(True))
            response = { 'status': 'ok'}
            response['routes'] = routes
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response)) 
        
    def __debug(self):
        locstart='Mountain View, CA'
        locend = 'San Gabriel, CA'        
        delivend = datetime.now()+timedelta(weeks=1)
        t = TrackerModel(driver=self.user_prefs.key, locstart=locstart, locend =locend, delivend=delivend)
        t = RouteUtils().setpoints(t,locstart,locend)
        t.put()
        return
        # data = json.loads(self.request.body)
        # try:
            # startlat = float(data['startlat'])
            # startlon = float(data['startlon'])

    def __debugcheckin(self):            
        loc = ndb.GeoPt(lat=34, lon=-119.08)
        point = TrackPt(loc=loc, locstr='Bumfuck, CA', created=datetime.now(), msg='I just ran over a reindeer, i think i might need medical assistance, please send help')
        routes = TrackerModel.by_driver(self.user_prefs.key)
        for r in routes:
            r.points.append(point)
            r.put()
        return
        