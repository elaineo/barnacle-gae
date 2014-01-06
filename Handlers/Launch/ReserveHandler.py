from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import mail

from Handlers.BaseHandler import *
from Handlers.SearchHandler import *
from Models.Launch.ResModel import *
from Models.RequestModel import *
from Models.Launch.Driver import *
from Utils.RouteUtils import *
from Utils.ValidUtils import *
from Utils.Defs import MV_geolat, MV_geolon, SG_geolat, SG_geolon, MV_string, SG_string

class ReserveHandler(BaseHandler):
    def get(self, action=None,key=None):
        if action=='driver' and key:
            self.__driverres(key)
        elif action=='json' and key:
            self.__jsondump(key)
        elif action=='edit' and key:
            self.params['key'] = key
            self.render('launch/fillitem.html', **self.params)
        else:
            self.params['route_title'] = 'Ship Your Stuff'
            self.render('launch/filllreq.html', **self.params)
                            
    def post(self, action=None,key=None):
        if (action=='driver') and key:
            self.__edit_res(key)
        elif (action=='search'):
            self.__search_drivers()
        elif (action=='filter') and key:
            self.__filter(key)       
        elif (action=='checkout') and key:
            self.__create_checkout(key)
        else:
            self.__create_res()
            
    def __search_drivers(self):
        # input from page 1, will go to page 3
        data = json.loads(unicode(self.request.body, errors='replace'))
        remoteip = self.request.remote_addr
        start, startstr = get_search_json(data,'start')
        dest, deststr = get_search_json(data,'dest') 
        distance = data.get('distance')
        enddate = self.request.get('reqdate')
        logging.info('Search req: '+startstr+' to '+deststr)
        if not start or not dest:
            #return error
            self.write('Invalid locations')
            return
        if enddate:
            delivend = parse_date(enddate)
        else:
            delivend = datetime.now()+timedelta(days=365)            
        # store this search
        sr = SearchEntry(remoteip = remoteip, start=start, dist = distance,
                    delivby = delivend,
                    dest=dest, locstart=startstr,locend=deststr).put()    
        
        self.response.headers['Content-Type'] = "application/json"
        response = { 'next' : '/res/edit/'+sr.urlsafe(),
                     'status': 'ok' }
        self.write(json.dumps(response))
    
    def __edit_res(self, key):
        # add more info to searchentry
        #data = json.loads(unicode(self.request.body, errors='replace'))        
        capacity = self.request.get('vcap')
        capacity = parse_unit(capacity)
        matches = self.request.get_all('dkey')

        res = ndb.Key(urlsafe=key).get()
        res.delivby = delivend
        res.capacity = capacity
        res.matches = [ndb.Key(urlsafe=m) for m in matches]
        res.put()
        #Next, upload img and make an offer -- we need suggested offer price
        self.params = res.params_fill(self.params)
        self.params['email'] = self.user_prefs.email
        self.params['update_url'] = '/res/checkout/'+key
        price, seed = priceEst(res, res.dist)
        self.params['rates'] = price
        self.params['routekey'] = key
        self.params['res_title'] = res.locstart + ' to ' + res.locend
        self.render('launch/request_review.html', **self.params)   
                    
        
    def __filter(self, key):
        # retrieve search, filter matching drivers
        res = ndb.Key(urlsafe=key).get()
        data = json.loads(unicode(self.request.body, errors='replace'))
        capacity = data.get('vcap')
        vcap = parse_unit(capacity)
        enddate = data.get('delivend')
        if enddate:
            delivend = parse_date(enddate)
        else:
            delivend = datetime.now().date()+timedelta(days=365)
        drivers = []
        for r in res.matches:
            route = r.get()
            if route.capacity > vcap and route.delivend <= delivend:
                p = route.to_search()
                d = Driver.by_userkey(route.userkey)
                p = d.params_fill(p)
                drivers.append(p)
        response = {'status': 'ok'}
        self.params['drivers'] = drivers  
        self.render('launch/drivermosaic.html', **self.params)   
        
    def __driverres(self,key):
        # retrieve search, find matching drivers
        dist = 100
        numres = 6
        delivend = datetime.now() + timedelta(days=365)
        res = ndb.Key(urlsafe=key).get()
        startresults = search_pathpts(dist,'ROUTE_INDEX',delivend.strftime('%Y-%m-%d'),'delivstart',res.start).results
        destresults = search_pathpts(dist,'ROUTE_INDEX',delivend.strftime('%Y-%m-%d'),'delivstart',res.dest).results
        results = search_intersect(startresults, destresults)                    
        keepers = []
        for c in results:
            startpt = field_byname(c, "start")
            dist0 = HaversinDist(res.start.lat,res.start.lon, startpt.latitude, startpt. longitude) 
            dist1 = HaversinDist(res.dest.lat,res.dest.lon, startpt.latitude, startpt.longitude)
            if dist0 < dist1:
                keepers.append(c)
        results = keepers
        logging.info(results)
        # if there are no drivers, redirect to next page to complete request
        drivers = []
        for r in results:
            route = ndb.Key(urlsafe=r.doc_id).get()
            res.matches.append(ndb.Key(urlsafe=r.doc_id))
            res.put()
            p = search_todict(r)
            p['capacity'] = route.capacity
            p['delivend'] = route.delivend.strftime('%m/%d/%Y')
            d = Driver.by_userkey(route.userkey)
            p = d.params_fill(p)
            drivers.append(p)
#rating, #completed, checkbox, vehicle, date arriving, insured, bank (tooltip)
#location, about            
        self.params['reskey'] = key
        self.params['drivers'] = drivers  
        self.params['today'] = datetime.now().strftime('%Y-%m-%d')
        self.params['res_title'] = res.locstart + ' to ' + res.locend
        self.render('launch/driverres.html', **self.params)    

    def __create_checkout(self,key):
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        items = self.request.get('items')
        email = self.request.get('email')
        if email and (email != self.user_prefs.email):
            u = self.user_prefs.key.get()
            u.email = email
            u.put()
        res = ndb.Key(urlsafe=key).get()
        # image upload
        img = self.request.get("file")
        # Create request
        stats = ReqStats(distance=int(res.dist))
        p = Request(userkey = self.user_prefs.key, capacity=res.capacity, 
            delivby=res.delivby, 
            start=res.start, dest=res.dest, locstart=res.locstart, 
            locend=res.locend, matches=res.matches, stats=stats)
        if img: 
            imgstore = ImageStore.new(img)
            imgstore.put()
            p.img_id = imgstore.key.id()
        p.rates = rates
        p.items = items
        p.put() 

        self.redirect('/checkout/'+p.key.urlsafe())                
        
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
            'profile_url': u.profile_url(),
            'profile_thumb': u.profile_image_url('small'),
            'deliv_completed': u.deliveries_completed(),
            'fbid' : u.userid,
            'key' : u.key.urlsafe()
        }
    if u.ins:
        p['insured'] = ins_str
        p['ins_email'] = ins_str_email
    else:
        p['insured'] = ''
        p['ins_email'] = ''
    if u.bank:
        p['bank'] = bank_str
    else:
        p['bank'] = ''
    return p
    
def fill_res_params(r):
    r = { 'reskey' : r.key.urlsafe() ,
          'price' : r.rates,
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
        