from google.appengine.ext import ndb
from Handlers.BaseHandler import *
from Models.RequestModel import Request
from Models.UserModels import UserPrefs
from Utils.SearchUtils import search_pathpts, search_todict, search_intersect, field_byname
import logging
import urllib
from Utils.data.citylist import cities


city_dict = {}
for c in cities:
    city_dict[c['city']] = ndb.GeoPt(c['lat'], c['lon'])


class SearchableRequestHandler(BaseHandler):
    def get(self, origin=None, dest=None):
        self.params['origin'] = urllib.unquote(origin)
        self.params['dest'] = urllib.unquote(dest)
        self.params['posts'] = self.get_requests(origin, dest)
        self.render('search_seo_requests.html', **self.params)

    def get_requests(self, origin, dest):
        """ Get routes that go from origin to destination
        TODO make search smarter so it will match routes in the vicinity of origin and destination, not just exact match
        """
        startstr = origin
        deststr = dest

        start = city_dict[origin]
        dest = city_dict[dest]

        dist=100
        delivstart = datetime.now()
        delivend = delivstart + timedelta(days=365)

        posts = []
        pathpts, precision = RouteUtils().estPath(start, dest, dist)
        results = Request.search_route(pathpts, delivstart, delivend, precision)
        for r in results:
            posts.append(r.to_search())

        return posts

