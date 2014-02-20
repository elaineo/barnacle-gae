from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import mail

from Handlers.BaseHandler import *
from Handlers.SearchHandler import *
from Models.User.Driver import *
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
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('launch/filllreq.html', **self.params)
                            
    def post(self, action=None,key=None):
        if (action=='search'):  #WHERE
            self.__where()
        elif (action=='edit') and key:  #WHAT
            self.__what(key)        
        elif (action=='driver') and key:
            self.__who(key)       
        else:
            self.__create_res()
            
    def __where(self):
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
    
    def __what(self, key):
        dist = 100
        numres = 6  #max results returned    
        # Turn the search entry into a request
        # Who cares about capacity, driver can figure it out
        category = self.request.get('category')
        category = parse_unit(category)
        items = self.request.get('items')
        img = self.request.get("file")
        
        res = ndb.Key(urlsafe=key).get()
        
        p = Request(parent=self.user_prefs.key, category=category, 
            items=items, delivby=res.delivby, start=res.start, dest=res.dest, 
            locstart=res.locstart, locend=res.locend)
        
        price, seed = priceEst(p, res.dist)
        stats = ReqStats(sugg_price=price, seed=seed, distance=int(res.dist))
        p.stats = stats
            
        if img: 
            imgstore = ImageStore.new(img).put()
            p.img_id = imgstore.id()
        
        p.put()
        # Next, display list of drivers
        startresults = search_pathpts(dist,'ROUTE_INDEX',p.delivby.strftime('%Y-%m-%d'),'delivstart',p.start).results
        destresults = search_pathpts(dist,'ROUTE_INDEX',p.delivby.strftime('%Y-%m-%d'),'delivstart',p.dest).results
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
        if len(results) < 1:
            self.redirect('/checkout/'+p.key.urlsafe())
        drivers = []
        for r in results:
            q = search_todict(r)
            route = ndb.Key(urlsafe=q['routekey']).get()    
            if route:
                q['capacity'] = route.capacity
                q['delivend'] = route.delivend.strftime('%m/%d/%Y')
                d = Driver.by_userkey(route.key.parent())
                q = d.params_fill()
                drivers.append(q)   
        self.params['reskey'] = p.key.urlsafe()
        self.params['drivers'] = drivers  
        self.render('launch/filldriver.html', **self.params)    
                    
         
        
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
        results = Driver.query()
        for d in results:
            # route = ndb.Key(urlsafe=r.doc_id).get()
            # res.matches.append(ndb.Key(urlsafe=r.doc_id))
            # res.put()
            # p = search_todict(r)
            # p['capacity'] = route.capacity
            # p['delivend'] = route.delivend.strftime('%m/%d/%Y')
            # d = Driver.by_userkey(route.key.parent())
            p={}
            p['capacity'] = 0
            p = d.params_fill()
            drivers.append(p)
#rating, #completed, checkbox, vehicle, date arriving, insured, bank (tooltip)
#location, about            
        self.params['reskey'] = key
        self.params['drivers'] = drivers  
        self.params['today'] = datetime.now().strftime('%Y-%m-%d')
        self.params['res_title'] = res.locstart + ' to ' + res.locend
        self.render('launch/filldriver.html', **self.params)    

    def __who(self,key):
        routes = self.request.get_all('dkey')
        res = ndb.Key(urlsafe=key).get()
        logging.info(routes)
        res.matches = [ndb.Key(urlsafe=r) for r in routes]
        # Notify these drivers
        self.redirect('/checkout/'+res.key.urlsafe())                
        
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