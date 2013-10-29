from Handlers.BaseHandler import *
from Models.RouteModel import Route
import urllib
import logging

class SitemapHandler(BaseHandler):
    """
    Sitemap for google to crawl urls for SEO
    """
    def get(self,action=None,key=None):
        buf = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        for route_url in self.get_route_urls():
            buf += '<url><loc>%s</loc></url>' % route_url
        buf += '</urlset>'
        self.response.headers['Content-Type'] = 'application/xml'
        self.write(buf)
        logging.info(buf)


    def get_route_urls(self):
        urls = []
        for route in Route.query():
            urls.append('http://' + urllib.quote('www.gobarnacle.com/route/from/' + route.locstart + '/to/' + route.locend))
        return urls
