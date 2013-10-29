from Handlers.BaseHandler import *
from Models.RouteModel import Route
from Models.UserModels import UserPrefs
import logging
import urllib


class SearchableRouteHandler(BaseHandler):
    """
    Make search engine crawlable route listing page
    """
    def get(self, origin=None, dest=None):
        self.params['origin'] = urllib.unquote(origin)
        self.params['dest'] = urllib.unquote(dest)
        self.params['posts'] = self.get_routes(origin, dest)
        self.render('search_seo.html', **self.params)

    def get_routes(self, origin, dest):
        """ Get routes that go from origin to destination
        TODO make search smarter so it will match routes in the vicinity of origin and destination, not just exact match
        """
        routes = []
        for r in Route.query(Route.locstart == origin, Route.locend == dest):
            user = r.userkey.get()
            d = {'first_name': user.first_name,
                'routekey': r.key.urlsafe(),
                'thumb_url': user.profile_image_url(mode="small"),
                'start': r.locstart,
                'dest': r.locend,
                'fbid': user.userid,
                'delivstart': r.delivstart.strftime('%b-%d-%y'),
                'delivend': r.delivstart.strftime('%b-%d-%y')}
            routes.append(d)
        return routes
