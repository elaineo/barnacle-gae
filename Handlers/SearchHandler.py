from Handlers.BaseHandler import *
from Models.RouteModel import *
from Models.RequestModel import SearchEntry
from Utils.RouteUtils import *
from Utils.SearchUtils import *
from Utils.SearchDocUtils import *
import logging
from google.appengine.ext import ndb
from Utils.ValidUtils import *
from datetime import *

class SearchHandler(BaseHandler):
    """ Search page """
    def get(self, action=None):
        if action=='request':
            self.render('search_requests.html', **self.params)
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
            delivend = delivstart + timedelta(days=1)
            
        start, startstr = self.__get_search_form('start')
        dest, deststr = self.__get_search_form('dest')            
        logging.info('Search req: '+startstr+' to '+deststr+' from '+startdate+' to '+enddate)
        if not start:
            self.params['delivstart'] = startdate
            self.params['delivend'] = enddate
            self.params['error_route'] = 'Invalid Location'
            self.render('search_requests.html', **self.params)
            return

        if dest:
            resultsstart = search_points_start_end(dist,'REQUEST_INDEX',delivend.strftime('%Y-%m-%d'),delivstart.strftime('%Y-%m-%d'),'delivby','start',start,'dest', dest)
            logging.info(resultsstart)
        else:
            resultsstart = search_points_start_end(dist,'REQUEST_INDEX',delivend.strftime('%Y-%m-%d'),delivstart.strftime('%Y-%m-%d'),'delivby','start',start,'dest')
            logging.info(resultsstart)
        route_ids=[]
        posts = []
        for doc in resultsstart.results:
            route_ids.append(doc.doc_id)
            d = search_todict(doc)
            p = {  'first_name': d['first_name'],
                    'post_url': d['post_url'],
                    'prof_url': d['prof_url'],
                    'thumb_url': d['thumb_url'],
                    'start': d['locstart'],
                    'dest': d['locend'],
                    'delivby': d['delivby'].strftime('%b-%d-%y')
                }
            # by  october, the other fields will be deprecated and we'll only
            # be using this
            try:
                routekey = d['routekey']
                userkey = d['userkey']
                p['fbid'] = ndb.Key(urlsafe=userkey).get().userid
            except:
                logging.info('Search Requests, old result')
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
        
        startresults = search_pathpts(dist,'ROUTE_INDEX',delivend.strftime('%Y-%m-%d'),'delivend',start).results
        destresults = search_pathpts(dist,'ROUTE_INDEX',delivend.strftime('%Y-%m-%d'),'delivend',dest).results
        results = search_intersect(startresults, destresults)
        keepers = []
        for c in results:
            startpt = field_byname(c, "start")
            destpt = field_byname(c, "dest")
            # shouldn't need this IF check after I refactor indices
            if destpt and startpt:
                dist0 = HaversinDist(start.lat,start.lon, startpt.latitude, startpt.longitude) 
                dist1 = HaversinDist(dest.lat,dest.lon, destpt.latitude, destpt.longitude)
                if dist0 < dist1:
                    keepers.append(c)
        results = keepers

        cl_startres = search_pathpts(dist,'PATHPT_INDEX',delivend.strftime('%Y-%m-%d'),'delivend',start).results
        cl_destres = search_pathpts(dist,'PATHPT_INDEX',delivend.strftime('%Y-%m-%d'),'delivend',dest).results
        #get intersection
        clresults = search_intersect(cl_startres, cl_destres)
        # Check for correct start/dest (startpt should be closer to start than dest)
        
        keepers = []
        for c in clresults:
            startpt = field_byname(c, "start")
            destpt = field_byname(c, "dest")
            if destpt and startpt:
                if HaversinDist(start.lat,start.lon, startpt.latitude, startpt.longitude) < HaversinDist(dest.lat,dest.lon, destpt.latitude, destpt.longitude):
                    keepers.append(c)
        clresults = keepers 
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
        self.params['posts'] = posts
        self.params['clposts'] = clposts
        self.render('searchres.html', **self.params)
    
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