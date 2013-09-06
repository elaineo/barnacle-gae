from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import mail

from Handlers.BaseHandler import *
from Models.Launch.ResModel import *
from Models.Launch.BarnacleModel import *
from Utils.RouteUtils import *
from Utils.ValidUtils import *
from Utils.Defs import MV_geolat, MV_geolon, SG_geolat, SG_geolon, MV_string, SG_string, ins_str, ins_str_email

class ReserveHandler(BaseHandler):
    def get(self, action=None,key=None):
        if action=='driver' and key:
            self.__driverres(key)
        elif action=='json' and key:
            self.__jsondump(key)
        else:
            self.params['route_title'] = 'Reserve a Delivery'
            self.render('launch/filllres.html', **self.params)
                            
    def post(self, action=None,key=None):
        if not self.user_prefs:
            self.redirect('/res#signin-box')
        if (action=='driver'):
            self.__create_checkout(key)
        else:
            self.__create_res()
            
    def __create_res(self):
        capacity = self.request.get('vcap')
        capacity = parse_unit(capacity)
        startdate = self.request.get('delivstart')
        enddate = self.request.get('delivend')
        rates = self.request.get('rates')
        rates = parse_rate(rates)     
        if rates <1:
            rates=20
        dropoff = bool(int(self.request.get('dropoff')))
        pickup = bool(int(self.request.get('pickup')))
        if dropoff:
            dropoffloc = self.request.get('dropTloc')
            if (dropoffloc == '0'):
                start = ndb.GeoPt(lat=MV_geolat,lon=MV_geolon)
                startstr = MV_string
            else:
                start = ndb.GeoPt(lat=SG_geolat,lon=SG_geolon)
                startstr = SG_string
        else:
            start, startstr = self.__get_map_form('start')
        if pickup:
            pickuploc = self.request.get('pickTloc')
            if (pickuploc == '0'):
                dest = ndb.GeoPt(lat=MV_geolat,lon=MV_geolon)
                deststr = MV_string
            else:
                dest = ndb.GeoPt(lat=SG_geolat,lon=SG_geolon)
                deststr = SG_string
        else:
            dest, deststr = self.__get_map_form('dest')

        
        if startdate:
            delivstart = parse_date(startdate)
        else:
            delivstart = datetime.now()
        if enddate:
            delivend = parse_date(enddate)
        else:
            delivend = datetime.now()+timedelta(weeks=1)
           
        p = ResModel( user=self.user_prefs.key, rates=rates, ratestemp=rates,
            locstart=startstr, locend=deststr, 
            start=start, dest=dest, capacity=capacity, 
            pickup=pickup, dropoff=dropoff, 
            delivstart=delivstart, delivend=delivend)            
        try:                
            p.put()            
            self.redirect('/res/driver/'+p.key.urlsafe())  
        except:
            self.params['error_route'] = 'Invalid Route'
            self.params['locstart'] = startstr
            self.params['locend'] = deststr
            self.params['delivstart'] = startdate
            self.params['delivend'] = enddate
            self.params['capacity'] = capacity
            self.params['route_title'] = 'Invalid Route'
            self.render('launch/filllres.html', **self.params)           
            
    def __create_checkout(self,key):
        dkey = self.request.get('dkey')
        rates = self.request.get('rates')
        res = ndb.Key(urlsafe=key).get()
        rates = parse_rate(rates)       
        res.rates = rates        
        res.driver = ndb.Key(urlsafe=dkey)
        res.put()
        self.redirect('/checkout/'+res.key.urlsafe())
        
    def __driverres(self,key):
        numres = 6
        users = BarnacleModel.query().fetch(numres)
        res = ndb.Key(urlsafe=key).get()
        drivers = []
        for u in users:
            p = fill_driver_params(u)
            p['rates']=res.ratestemp+u.seed
            drivers.append(p)
        self.params['reskey'] = key
        self.params['drivers'] = drivers            
        self.render('launch/driverres.html', **self.params)    
        
        
    def __jsondump(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()
        except: 
            self.abort(400)
        rdump = RouteUtils().dumppts([res.start,res.dest])                
        self.response.headers['Content-Type'] = "application/json"                
        self.write(rdump)              
                        
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

def fill_driver_params(u): 
    p = {  'first_name': u.first_name,
            'prof_url': u.profile_url(),
            'thumb_url': u.profile_image_url('small'),
            'deliveries': u.deliveries_completed(),
            'fbid' : u.userid,
            'key' : u.key.urlsafe()
        }
    if u.ins:
        p['insured'] = ins_str
        p['ins_email'] = ins_str_email
    else:
        p['insured'] = ''
        p['ins_email'] = ''
    return p

def fill_res_params(r):
    r = { 'reskey' : r.key.urlsafe() ,
          'rates' : r.rates,
          'locstart' : r.locstart,
          'locend' : r.locend,
          'details' : r.details,
          'delivstart' : r.delivstart.strftime('%m/%d/%Y'),
          'delivend' : r.delivend.strftime('%m/%d/%Y'),
          'capacity' : r.capacity
       }
    return r
    
def fill_route_params(key,is_route=False):
    p = ndb.Key(urlsafe=key).get()
    u = p.userkey.get()
    params = {
        'profile_url' : u.profile_url(),
        'reserve_url' : p.reserve_url(),
        'edit_url' : p.edit_url(),
        'delete_url':p.delete_url(),        
        'first_name': u.nickname(),
        'routekey' : key,
        'locstart' : p.locstart,
        'locend' : p.locend,
        'num_confirmed' : p.num_confirmed(),
        'msg_ok' : True #(0 in u.get_notify())
        }
    if is_route:
        params.update({ 'details' : p.details,
                        'capacity' : p.capacity,
                        'num_requests' : p.num_requests(),
                        'sugg_rate' :p.suggest_rate(),
                        'delivstart' : p.delivstart.strftime('%m/%d/%Y'),
                        'delivend' : p.delivend.strftime('%m/%d/%Y') })
        params.update(p.gen_repeat())
    else:
        params.update({ 'items' : p.items,
                        'num_offers' : p.num_offers(),
                        'rates' : p.rates,
                        'delivby' : p.delivby.strftime('%m/%d/%Y') })    
    message_url = '/message?'
    message_url += 'receiver=' + u.key.urlsafe() + '&subject=' +p.locstart+' to ' +p.locend
    params['message_url'] = message_url
    return params
        