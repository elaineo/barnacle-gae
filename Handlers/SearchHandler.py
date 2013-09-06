from Handlers.BaseHandler import *
from Models.RouteModel import *
from Models.RequestModel import SearchEntry
from Utils.RouteUtils import *
from Utils.SearchUtils import *
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
        dist = 100  ## IMPROVE THIS
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
        results = search_points_end(dist,'ROUTE_INDEX',delivend.strftime('%Y-%m-%d'),'delivend','start',start,'dest',dest)

        clresults = search_points_end(dist,'CL_INDEX',delivend.strftime('%Y-%m-%d'),'delivend','start',start,'dest',dest)        

        # store this search
        sr = SearchEntry(remoteip = remoteip, delivby=delivend, start=start, 
                    dest=dest, locstart=startstr,locend=deststr).put()
        route_ids=[]
        posts = []
        for doc in results.results:
            logging.info(doc)
            route_ids.append(doc.doc_id)
            d = search_todict(doc)
            try:
                p = {  'first_name': d['first_name'],
                        'post_url': d['post_url'],
                        'prof_url': d['prof_url'],
                        'thumb_url': d['thumb_url'],
                        'start': d['locstart'],
                        'dest': d['locend'],
                        'delivstart': d['delivstart'].strftime('%b-%d-%y'),
                        'delivend': d['delivend'].strftime('%b-%d-%y')
                    }
                posts.append(p)
            except:
                continue
        cl_ids=[]
        clposts = []
        for doc in clresults.results:
            logging.info(doc)
            cl_ids.append(doc.doc_id)
            d = search_todict(doc)
            p = {   'post_url': d['post_url'],
                    'start': d['locstart'],
                    'dest': d['locend'],
                    'delivend': d['delivend'].strftime('%b-%d-%y')
                }
            clposts.append(p)
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