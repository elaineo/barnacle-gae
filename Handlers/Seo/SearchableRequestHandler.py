from datetime import *
from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Models.Post.Request import Request
from Utils.SearchUtils import search_pathpts, search_todict, search_intersect, field_byname, search_points_start
from Utils.RouteUtils import *
import logging
import urllib
from Utils.data.citylist import cities


city_dict = {}
for c in cities:
    city_dict[c['city']] = ndb.GeoPt(c['lat'], c['lon'])


class SearchableRequestHandler(BaseHandler):
    def get(self, origin=None, dest=None):
        if origin:
            self.params['origin'] = urllib.unquote(origin)
        if dest:
            self.params['dest'] = urllib.unquote(dest)
        self.params['today'] = datetime.now().strftime('%Y-%m-%d')
        if origin == None:
            try:
                posts, center = self.__get_reqs_to(dest)            
                posts = dump_results(posts) 
                self.params['posts'] = [p.to_search() for p in posts]
                rdump = RouteUtils().dumpreqs(posts, dest=True)
                self.params['markers'] = rdump['markers']
                self.params['center'] = center
            except:
                pass
            self.render('search/seo_requests_to.html', **self.params)
        elif origin.upper() == 'USA':
            #return everything
            posts = Request.query(Request.dead==0)
            self.params['posts'] = [p.to_search() for p in posts]
            rdump = RouteUtils().dumpreqs(posts)
            self.params['markers'] = rdump['markers']
            self.params['center'] = [40,-99]
            self.render('search/seo_requests_all.html', **self.params)            
        elif dest == None:
            try:
                posts, center = self.__get_reqs_from(origin)            
                posts = dump_results(posts) 
                self.params['posts'] = [p.to_search() for p in posts]
                rdump = RouteUtils().dumpreqs(posts, dest=False)
                self.params['markers'] = rdump['markers']
                self.params['center'] = center
            except:
                pass
            self.render('search/seo_requests_from.html', **self.params)
        else:
            try:
                posts, center = self.__get_reqs(origin, dest)
                self.params['posts'] = [p.to_search() for p in posts]
                rdump = RouteUtils().dumpreqs(posts)
                self.params['markers'] = rdump['markers']
                self.params['center'] = center
            except:
                pass
            self.render('search/seo_requests.html', **self.params)
    
    def post(self,origin=None):
        if origin=='citylut':
            self.__city_lookup()
        elif origin=='reqseo':
            self.__search_requests_seo()
    
    def __get_reqs(self, origin, dest):
        if (origin not in city_dict) or (dest not in city_dict):
            return None, None   
        startstr = origin
        deststr = dest

        start = city_dict[origin]
        dest = city_dict[dest]

        dist=100
        delivstart = datetime.now()
        delivend = delivstart + timedelta(days=365)

        pathpts, precision = RouteUtils().estPath(start, dest, dist)
        results = Request.search_route(pathpts, delivstart, delivend, precision)
        center = findCenter([start,dest])
        return results, center
        
    def __get_reqs_to(self, dest):
        if dest not in city_dict:
            return []    
        deststr = dest

        dest = city_dict[dest]

        dist=100
        delivstart = datetime.now()
        delivend = delivstart + timedelta(days=365)

        results = search_points_start(dist,'REQUEST_INDEX',delivend.strftime('%Y-%m-%d'),delivstart.strftime('%Y-%m-%d'),'delivby','dest',dest)

        return results, [dest.lat,dest.lon]

    def __get_reqs_from(self, start):
        if start not in city_dict:
            return []    
        startstr = start

        start = city_dict[start]

        dist=100
        delivstart = datetime.now()
        delivend = delivstart + timedelta(days=365)

        results = search_points_start(dist,'REQUEST_INDEX',delivend.strftime('%Y-%m-%d'),delivstart.strftime('%Y-%m-%d'),'delivby','start',start)

        return results, [start.lat,start.lon]

    ''' crap for later '''
    def __city_lookup(self):            
        self.response.headers['Content-Type'] = "application/json"
        start,startstr = self.__get_search_form('start')
        # destination is optional. Make two calls if you want.
        dest,deststr = self.__get_search_form('dest')   
        ## find nearest major cities
        startc = search_points(start, 'loc', CITY_INDEX)
        destc = search_points(dest, 'loc', CITY_INDEX)
        response = {}
        for doc in startc.results:
            d = search_todict(doc)
            d['loc'] = [d['loc'].latitude, d['loc'].longitude]
            response['start'] = d
        for doc in destc.results:
            d = search_todict(doc)
            d['loc'] = [d['loc'].latitude, d['loc'].longitude]
            response['dest'] = d
        self.write(json.dumps(response))
        
    def __search_requests_seo(self):
        self.response.headers['Content-Type'] = "application/json"
        start,startstr = self.__get_search_form('start')
        if not start:
            r = Request.query()
            rdump = RouteUtils().dumpreqs(r)
            self.write(json.dumps(rdump))
            return
        # this is optional
        dest,deststr = self.__get_search_form('dest')     

        dist=100
        delivstart = datetime.now()
        delivend = delivstart + timedelta(days=365)

        posts = []
        if dest:            
            ### Get a set of low-res pathpts
            pathpts, precision = RouteUtils().estPath(start, dest,dist)
            pp = []
            for p in pathpts:
                pp.append([p.lat,p.lon])
            results = Request.search_route(pathpts, delivstart, delivend, precision)
            rdump = RouteUtils().dumpreqs(results)
            rdump['waypts'] = pp
        else:
            results = search_points_start(dist,'REQUEST_INDEX',delivend.strftime('%Y-%m-%d'),delivstart.strftime('%Y-%m-%d'),'delivby','start',start)

            r = []
            for doc in results.results:
                r.append(ndb.Key(urlsafe=doc.doc_id).get())
            rdump = RouteUtils().dumpreqs(r)
        self.write(json.dumps(rdump))
        
        
def dump_results(results):
    posts = []
    for doc in results.results:
        d = search_todict(doc)
        posts.append(d)        
    return [ndb.Key(urlsafe=p['routekey']).get() for p in posts]