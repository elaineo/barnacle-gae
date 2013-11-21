from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Models.RouteModel import Route
from Models.UserModels import UserPrefs
from Utils.SearchUtils import search_pathpts, search_todict, search_intersect, field_byname
import logging
import urllib
from Utils.data.citylist import cities


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
        if origin == None:
            self.params['posts'] = self.get_routes_to(dest)
            self.render('search_seo_to.html', **self.params)
        elif dest == None:
            self.params['posts'] = self.get_routes_from(origin)
            self.render('search_seo_from.html', **self.params)
        else:
            self.params['posts'] = self.get_routes(origin, dest)
            self.render('search_seo.html', **self.params)

    def get_routes_from(self, origin):
        if origin not in city_dict:
            return []
        start = city_dict[origin]
        delivend = datetime.now() + timedelta(days=365)
        logging.info(start)
        dist = 10  # miles
        results = search_pathpts(
            dist, 'ROUTE_INDEX', delivend.strftime('%Y-%m-%d'), 'delivstart', start).results
        keepers = []
        for c in results:
            startpt = field_byname(c, "start")
            dist0 = HaversinDist(
                start.lat, start.lon, startpt.latitude, startpt.longitude)
            logging.info(startpt)
            logging.info(dist0)
            if dist0 < dist:
                keepers.append(c)
        results = keepers
        return self.results_to_post(results)

    def get_routes_to(self, dest):
        if dest not in city_dict:
            return []
        dest = city_dict[dest]
        delivend = datetime.now() + timedelta(days=365)
        dist = 10
        results = search_pathpts(
            dist, 'ROUTE_INDEX', delivend.strftime('%Y-%m-%d'), 'delivstart', dest).results
        logging.info(results)
        keepers = []
        for c in results:
            startpt = field_byname(c, "dest")
            dist1 = HaversinDist(
                dest.lat, dest.lon, startpt.latitude, startpt.longitude)
            if dist1 < dist:
                keepers.append(c)
        results = keepers
        return self.results_to_post(results)

    def results_to_post(self, results):
        """ convert search results to posts """
        posts = []
        for doc in results:
            d = search_todict(doc)
            try:
                p = {'first_name': d['first_name'],
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
        return posts

    def get_routes(self, origin, dest):
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
        results = keepers

        return self.results_to_post(results)
