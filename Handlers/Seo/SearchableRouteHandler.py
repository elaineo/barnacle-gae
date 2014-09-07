from datetime import *
from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Models.Post.Route import Route
from Utils.RouteUtils import *
from Utils.SearchUtils import search_pathpts, search_todict, search_intersect, field_byname
import logging
import urllib
from Utils.data.citylist import cities
from google.appengine.api import memcache


city_dict = {}
for c in cities:
    city_dict[c['city']] = ndb.GeoPt(c['lat'], c['lon'])


class SearchableRouteHandler(BaseHandler):

    """
    Make search engine crawlable route listing page
    """

    def get(self, origin=None, dest=None):
        if origin:
            self.params['origin'] = urllib.unquote(origin)
        if dest:
            self.params['dest'] = urllib.unquote(dest)
        self.params['today'] = datetime.now().strftime('%Y-%m-%d')
        if origin == None:
            try:
                posts, center = self.__get_routes_to(dest)
                posts = dump_results(posts)
                self.params['center'] = center
                if len(posts) > 0:
                    self.params['posts'] = [p.to_search() for p in posts]
                    rdump = RouteUtils.dumpall(posts)
                    self.params['center'] = rdump['center']
                    self.params['paths'] = rdump['paths']
            except:
                pass
            self.render('search/seo_route_to.html', **self.params)
        elif origin.upper() == 'USA':
            #return everything
            ROUTE_USA_KEY = 'route_from_usa'
            routes_usa = memcache.get(ROUTE_USA_KEY)
            if routes_usa:
                return self.write(routes_usa)
            else:
                posts = Route.query(Route.dead==0)
                self.params['posts'] = [p.to_search() for p in posts]
                rdump = RouteUtils.dumpall(posts)
                self.params['center'] = rdump['center']
                self.params['paths'] = rdump['paths']
                routes_usa = self.render_str('search/seo_route_all.html', **self.params)
                memcache.add(key=ROUTE_USA_KEY, value=routes_usa)
                self.write(routes_usa)
        elif dest == None:
            try:
                posts, center = self.__get_routes_from(origin)
                posts = dump_results(posts)
                self.params['center'] = center
                if len(posts) > 0:
                    self.params['posts'] = [p.to_search() for p in posts]
                    rdump = RouteUtils.dumpall(posts)
                    self.params['center'] = rdump['center']
                    self.params['paths'] = rdump['paths']
            except:
                pass
            self.render('search/seo_route_from.html', **self.params)
        else:
            try:
                posts, center = self.__get_routes(origin, dest)
                posts = dump_results(posts)
                self.params['center'] = center
                if len(posts) > 0:
                    self.params['posts'] = [p.to_search() for p in posts]
                    rdump = RouteUtils.dumpall(posts)
                    self.params['center'] = rdump['center']
                    self.params['paths'] = rdump['paths']
            except:
                pass
            self.render('search/seo_route.html', **self.params)

    def __get_routes_from(self, origin):
        if origin not in city_dict:
            return []
        start = city_dict[origin]
        delivend = datetime.now() + timedelta(days=365)
        dist = 100  # miles
        results = search_pathpts(
            dist, 'ROUTE_INDEX', delivend.strftime('%Y-%m-%d'), 'delivstart', start).results
        keepers = []
        for c in results:
            startpt = field_byname(c, "start")
            dist0 = HaversinDist(
                start.lat, start.lon, startpt.latitude, startpt.longitude)
            if dist0 < dist:
                keepers.append(c)
        return keepers, [start.lat,start.lon]

    def __get_routes_to(self, dest):
        if dest not in city_dict:
            return []
        dest = city_dict[dest]
        delivend = datetime.now() + timedelta(days=365)
        dist = 100
        results = search_pathpts(
            dist, 'ROUTE_INDEX', delivend.strftime('%Y-%m-%d'), 'delivstart', dest).results
        keepers = []
        for c in results:
            startpt = field_byname(c, "dest")
            dist1 = HaversinDist(
                dest.lat, dest.lon, startpt.latitude, startpt.longitude)
            if dist1 < dist:
                keepers.append(c)
        return keepers, [dest.lat,dest.lon]

    def __get_routes(self, origin, dest):
        """ Get routes that go from origin to destination
        TODO make search smarter so it will match routes in the vicinity of origin and destination, not just exact match
        """
        delivend = datetime.now() + timedelta(days=365)

        startstr = origin
        deststr = dest

        if (origin not in city_dict) or (dest not in city_dict):
            return []

        start = city_dict[origin]
        dest = city_dict[dest]

        dist = HaversinDist(start.lat, start.lon, dest.lat, dest.lon) / 10
        startresults = search_pathpts(
            dist, 'ROUTE_INDEX', delivend.strftime('%Y-%m-%d'), 'delivstart', start).results
        destresults = search_pathpts(
            dist, 'ROUTE_INDEX', delivend.strftime('%Y-%m-%d'), 'delivstart', dest).results
        results = search_intersect(startresults, destresults)
        keepers = []
        for c in results:
            startpt = field_byname(c, "start")
            dist0 = HaversinDist(
                start.lat, start.lon, startpt.latitude, startpt.longitude)
            dist1 = HaversinDist(
                dest.lat, dest.lon, startpt.latitude, startpt.longitude)
            if dist0 < dist1:
                keepers.append(c)
        center = findCenter([start,dest])
        return keepers, center

def dump_results(results):
    posts = []
    for doc in results:
        d = search_todict(doc)
        posts.append(d)
    return [ndb.Key(urlsafe=p['routekey']).get() for p in posts]
