from Handlers.BaseHandler import *
from Models.RouteModel import *
from Models.RequestModel import *
from Utils.RouteUtils import *
from Utils.SearchUtils import *
from Utils.SearchScraped import *
from Utils.SearchDocUtils import *
import logging
from google.appengine.ext import ndb
from Utils.ValidUtils import *
from datetime import *

class SearchHandler(BaseHandler):
    """ Search page """
    def get(self, action=None, key=None):
        if action=='request':
            self.render('search_requests.html', **self.params)
        elif action=='scrapez':
            sdump = {}
            if not key:
                return
            try:
                search=ndb.Key(urlsafe=key).get()
                sdump['results'] = self.__search_zscrape(search)                
            except:
                sdump = {'status' : 'fail'}
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(sdump))
        elif action=='scrapecl':
            sdump = {}
            if not key:
                return
            try:
                search=ndb.Key(urlsafe=key).get()
                sdump['results'] = self.__search_clscrape(search)                
            except:
                sdump = {'status' : 'fail'}
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(sdump))            
        else:
            self.render('search.html', **self.params)
        
    def post(self,action=None):
        if action=='request':
            self.__search_requests()
        else:
            self.__search_routes()

    def __search_requests(self):
        dist = self.request.get('dist')
        if not dist:
            dist = 100
        dist = int(dist)
        startdate = self.request.get('startdate')
        enddate = self.request.get('enddate')
        if startdate:
            delivstart = parse_date(startdate)
        else:
            delivstart = datetime.now()
        if enddate:
            delivend = parse_date(enddate)
        else:
            delivend = delivstart + timedelta(days=90)
            
        start, startstr = self.__get_search_form('start')
        dest, deststr = self.__get_search_form('dest')            
        logging.info('Search req: '+startstr+' to '+deststr+' from '+startdate+' to '+enddate)
        if not start:
            self.params['delivstart'] = startdate
            self.params['delivend'] = enddate
            self.params['error_route'] = 'Invalid Location'
            self.render('search_requests.html', **self.params)
            return

        posts = []
        ## Change this to a query
        if dest:
            ### Get a set of low-res pathpts
            pathpts, precision = RouteUtils().estPath(start, dest,dist)
            results = Request.search_route(pathpts, delivstart, delivend, precision)
            for r in results:
                posts.append(r.to_search())
        else:
            results = search_points_start(dist,'REQUEST_INDEX',delivend.strftime('%Y-%m-%d'),delivstart.strftime('%Y-%m-%d'),'delivby','start',start)
            logging.info(results)

            for doc in results.results:
                d = search_todict(doc)
                p = {  'first_name': d['first_name'],
                        'thumb_url': d['thumb_url'],
                        'start': d['locstart'],
                        'dest': d['locend'],
                        'delivby': d['delivby'].strftime('%b-%d-%y'),
                        'fbid' : d['fbid'],
                        'routekey': d['routekey']
                    }
                posts.append(p)

        self.params['posts'] = posts
        self.render('searchqres.html', **self.params)
            
    def __search_routes(self):        
        enddate = self.request.get('enddate')
        remoteip = self.request.remote_addr
        if enddate:
            delivend = parse_date(enddate)
        else:
            delivend = datetime.now() + timedelta(days=365)
        
        start, startstr = self.__get_search_form('start')
        dest, deststr = self.__get_search_form('dest')
        logging.info('Search req: '+startstr+' to '+deststr+' by '+enddate)         
        if not start or not dest:          
            self.params['error_route'] = 'Invalid Route'
            self.render('search.html', **self.params)
            return           
            
        dist = HaversinDist(start.lat,start.lon,dest.lat,dest.lon)/10
        
        startresults = search_pathpts(dist,'ROUTE_INDEX',delivend.strftime('%Y-%m-%d'),'delivstart',start).results
        destresults = search_pathpts(dist,'ROUTE_INDEX',delivend.strftime('%Y-%m-%d'),'delivstart',dest).results
        results = search_intersect(startresults, destresults)
        keepers = []
        for c in results:
            startpt = field_byname(c, "start")
            dist0 = HaversinDist(start.lat,start.lon, startpt.latitude, startpt.longitude) 
            dist1 = HaversinDist(dest.lat,dest.lon, startpt.latitude, startpt.longitude)
            if dist0 < dist1:
                keepers.append(c)
        results = keepers
        logging.info(results)
        
        # store this search
        sr = SearchEntry(remoteip = remoteip, delivby=delivend, start=start, 
                    dest=dest, locstart=startstr,locend=deststr).put()
                    
        posts = []
        for doc in results:
            d = search_todict(doc)
            try:
                p = {  'first_name': d['first_name'],
                        'routekey': d['routekey'],
                        'thumb_url': d['thumb_url'],
                        'start': d['locstart'],
                        'dest': d['locend'],
                        'fbid': d['fbid'],
                        'delivstart': d['delivstart'].strftime('%b-%d-%y'),
                        'delivend': d['delivend'].strftime('%b-%d-%y')
                    }
                posts.append(p)
            except:
                continue
                
        self.params['posts'] = posts
        self.params['searchkey'] = sr.urlsafe()
        self.render('searchfrag.html', **self.params)
        
    def __search_clscrape(self, sr):
        startres = search_pathpts(sr.dist,'PATHPT_INDEX',sr.delivby.strftime('%Y-%m-%d'),'delivend',sr.start).results
        destres = search_pathpts(sr.dist,'PATHPT_INDEX',sr.delivby.strftime('%Y-%m-%d'),'delivend',sr.dest).results
        #get intersection
        results = search_intersect(startres, destres)
        # Check for correct start/dest (startpt should be closer to start than dest)
        
        keepers = []
        for c in results:
            startpt = field_byname(c, "start")
            if startpt:
                if HaversinDist(sr.start.lat,sr.start.lon, startpt.latitude, startpt.longitude) < HaversinDist(sr.dest.lat,sr.dest.lon, startpt.latitude, startpt.longitude):
                    keepers.append(c)
        clresults = keepers 
        clposts = []
        for doc in clresults:
            d = search_todict(doc)
            try:
                p = {  'routekey': d['routekey'],
                        'start': d['locstart'],
                        'dest': d['locend'],
                        'delivend': d['delivend'].strftime('%b-%d-%y')
                    }   
                clposts.append(p)
            except:
                continue      
        return clposts
            
    
    def __search_zscrape(self, sr):
        startres = search_pathpts(sr.dist,'ZIM_INDEX',sr.delivby.strftime('%Y-%m-%d'),'delivend',sr.start).results
        destres = search_pathpts(sr.dist,'ZIM_INDEX',sr.delivby.strftime('%Y-%m-%d'),'delivend',sr.dest).results
        #get intersection
        results = search_intersect(startres, destres)

        keepers = []
        for z in results:
            startpt = field_byname(z, "start")
            if startpt:
                if HaversinDist(sr.start.lat,sr.start.lon, startpt.latitude, startpt.longitude) < HaversinDist(sr.dest.lat,sr.dest.lon, startpt.latitude, startpt.longitude):
                    keepers.append(z)
        zresults = keepers                
        
        zposts = []
        for doc in zresults:
            d = search_todict(doc)
            try:
                p = {   'routekey': d['routekey'],
                        'start': d['locstart'],
                        'dest': d['locend'],
                        'fbid': d['fbid'],
                        'delivend': d['delivend'].strftime('%b-%d-%y')
                    }
                zposts.append(p)
            except:
                continue        
        return zposts
    
    def __get_search_form(self,pt):
        ptlat = self.request.get(pt+'lat')
        ptlon = self.request.get(pt+'lon')
        ptstr = self.request.get(pt)
        if not ptlat or not ptlon:            
            if ptstr:
                ptg = RouteUtils().getGeoLoc(ptstr)[0]
            else:
                ptg = None
        else:
            ptg = ndb.GeoPt(lat=ptlat,lon=ptlon)    
        return ptg, ptstr    