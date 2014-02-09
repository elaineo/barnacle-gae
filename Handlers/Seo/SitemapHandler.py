from Handlers.BaseHandler import *
from Models.RouteModel import Route
from Models.RequestModel import Request
from google.appengine.ext import ndb
from Utils.SearchUtils import search_points
from Utils.SearchDocUtils import closest_city
import urllib
import logging

# Generate sitemap.xml


def list_to_url_xml(urls, priority = None):
    """ turns a list of urls into url xml with priority
    """
    if priority is not None:
        priority = '<priority>%1.2f</priority>' % priority
    else:
        priority = ''
    return '\n'.join(['<url><loc>%s</loc>%s</url>' % (url, priority) for url in urls])


class SitemapHandler(BaseHandler):
    """
    Sitemap for google to crawl urls for SEO
    """
    def get(self,action=None,key=None):
        buf = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        buf += list_to_url_xml(self.get_home_urls(), priority = 0.6)
        buf += list_to_url_xml(self.get_route_urls())
        buf += list_to_url_xml(self.get_request_urls())
        buf += '</urlset>'
        self.response.headers['Content-Type'] = 'application/xml'
        self.write(buf)

    def get_home_urls(self):
        return ['http://www.gobarnalce.com/about', 'http://www.gobarnalce.com/how', 'http://www.gobarnalce.com/blog']

    def get_route_urls(self):
        urls = []
        for route in Route.query():
            start_nearest_city = closest_city(route.pathpts[0])['city']
            end_nearest_city = closest_city(route.pathpts[-1])['city']
            urls.append('http://' + urllib.quote('www.gobarnacle.com/route/from/' + start_nearest_city + '/to/' + end_nearest_city))
            urls.append('http://' + urllib.quote('www.gobarnacle.com/route/from/' + start_nearest_city))
            urls.append('http://' + urllib.quote('www.gobarnacle.com/route/to/' + end_nearest_city))
        return set(urls)

    def get_request_urls(self):
        urls = []
        for request in Request.query():
            start_nearest_city = closest_city(request.start)['city']
            end_nearest_city = closest_city(request.dest)['city']
            urls.append('http://' + urllib.quote('www.gobarnacle.com/request/from/' + start_nearest_city + '/to/' + end_nearest_city))
            urls.append('http://' + urllib.quote('www.gobarnacle.com/request/from/' + start_nearest_city))
            urls.append('http://' + urllib.quote('www.gobarnacle.com/request/to/' + end_nearest_city))
        return set(urls)
