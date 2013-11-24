from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Models.RequestModel import Request
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
        if origin == None:
            posts, center = self.__get_reqs_to(dest)            
            posts = dump_results(posts) 
            self.params['posts'] = [p.to_search() for p in posts]
            rdump = RouteUtils().dumpreqs(posts, dest=True)
            self.params['markers'] = rdump['markers']
            self.params['center'] = center
            self.render('search/seo_requests_to.html', **self.params)
        elif origin.upper() == 'USA':
            #return everything
            posts = Request.get_all()
            self.params['posts'] = [p.to_search() for p in posts]
            rdump = RouteUtils().dumpreqs(posts)
            self.params['markers'] = rdump['markers']
            self.params['center'] = [40,-99]
            self.render('search/seo_requests_all.html', **self.params)            
        elif dest == None:
            posts, center = self.__get_reqs_from(origin)            
            posts = dump_results(posts) 
            self.params['posts'] = [p.to_search() for p in posts]
            rdump = RouteUtils().dumpreqs(posts, dest=False)
            self.params['markers'] = rdump['markers']
            self.params['center'] = center
            self.render('search/seo_requests_from.html', **self.params)
        else:
            posts, center = self.__get_reqs(origin, dest)
            self.params['posts'] = [p.to_search() for p in posts]
            rdump = RouteUtils().dumpreqs(posts)
            self.params['markers'] = rdump['markers']
            self.params['center'] = center
            self.render('search/seo_requests.html', **self.params)
    
    def __get_reqs(self, origin, dest):
        if (origin not in city_dict) or (dest not in city_dict):
            return []    
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
        
def dump_results(results):
    posts = []
    for doc in results.results:
        d = search_todict(doc)
        posts.append(d)        
    return [ndb.Key(urlsafe=p['routekey']).get() for p in posts]