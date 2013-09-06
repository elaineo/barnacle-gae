from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import mail


from Handlers.BaseHandler import *
from Models.Launch.ReqModel import *
from Utils.RouteUtils import *
from Utils.ValidUtils import *
from Utils.Defs import MV_geolat, MV_geolon, SG_geolat, SG_geolon, MV_string, SG_string, ins_str

class RequestHandler(BaseHandler):
    def get(self, action=None,key=None):
        self.params['route_title'] = 'Submit a Delivery Request'
        self.render('launch/filllreq.html', **self.params)        
    
    def post(self, action=None,key=None):
        if not self.user_prefs:
            self.redirect('/request#signin-box')
        self.__create_req()
            
    def __create_req(self):
        capacity = self.request.get('vcap')
        capacity = parse_unit(capacity)
        startdate = self.request.get('delivstart')
        enddate = self.request.get('delivend')

        start, startstr = self.__get_map_form('start')
        dest, deststr = self.__get_map_form('dest')

        details = self.request.get('details')
        email = self.request.get('email')
        
        if startdate:
            delivstart = parse_date(startdate)
        else:
            delivstart = datetime.now()
        if enddate:
            delivend = parse_date(enddate)
        else:
            delivend = datetime.now()+timedelta(weeks=1)
           
        p = ReqModel( user=self.user_prefs.key,
            locstart=startstr, locend=deststr, 
            start=start, dest=dest, capacity=capacity, 
            delivstart=delivstart, delivend=delivend, details=details,
            email=email)            
        try:                
            p.put()            
            self.render('/launch/thanksreq.html', **self.params)  
        except:
            self.params['error_route'] = 'Invalid Route'
            self.params['locstart'] = startstr
            self.params['locend'] = deststr
            self.params['delivstart'] = startdate
            self.params['delivend'] = enddate
            self.params['capacity'] = capacity
            self.params['email'] = email
            self.params['details'] = details
            self.params['route_title'] = 'Invalid Route'
            self.render('launch/filllreq.html', **self.params)                       
            
            
    def __get_map_form(self,pt):
        ptlat = self.request.get(pt+'lat')
        ptlon = self.request.get(pt+'lon')
        ptstr = self.request.get(pt+'str')        
        if not ptstr or not ptlat or not ptlon:
            ptstr = self.request.get(pt)
            if ptstr:
                ptg = RouteUtils().getGeoLoc(ptstr)[0]
            else:
                ptg = None
        else:
            ptg = ndb.GeoPt(lat=ptlat,lon=ptlon)    
        return ptg, ptstr
