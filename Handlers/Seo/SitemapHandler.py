from Handlers.BaseHandler import *
from Models.Post.Route import Route
from Models.Post.Request import Request
from Models.Seo.Sitemap import *
from google.appengine.ext import ndb
from Utils.SearchUtils import search_points
from Utils.SearchDocUtils import closest_city
import urllib
import logging

"""
For serving /sitemap.xml
"""

def list_to_url_xml(urls, priority = None):
    """ turns a list of urls into url xml with priority
    """
    if priority is not None:
        priority = '<priority>%1.2f</priority>' % priority
    else:
        priority = ''
    return '\n'.join(['<url><loc>%s</loc>%s</url>' % (url, priority) for url in urls])


class SitemapGenerationHandler(BaseHandler):
    """
    Generate sitemap because it takes too long to generate on the fly
    """
    def get(self,action=None,key=None):
        buf = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        buf += list_to_url_xml(self.get_home_urls(), priority = 0.6)
        buf += list_to_url_xml(self.get_route_urls())
        buf += list_to_url_xml(self.get_request_urls())
        buf += '</urlset>'
        Sitemap.update_contents(buf)

    def get_home_urls(self):
        return ['http://www.gobarnacle.com/about', 'http://www.gobarnacle.com/how', 'http://www.gobarnacle.com/blog']

    def get_route_urls(self):
        urls = []
        for route in Route.query():
            if len(route.pathpts) > 1:
                try:
                    start_nearest_city = closest_city(route.start)['city']
                    end_nearest_city = closest_city(route.dest)['city']
                    urls.append('http://' + urllib.quote('www.gobarnacle.com/route/from/' + start_nearest_city + '/to/' + end_nearest_city))
                    urls.append('http://' + urllib.quote('www.gobarnacle.com/route/from/' + start_nearest_city))
                    urls.append('http://' + urllib.quote('www.gobarnacle.com/route/to/' + end_nearest_city))
                except:
                    logging.warn('error for route: ' + route.key)
        return set(urls)

    def get_request_urls(self):
        urls = []
        for request in Request.query():
            logging.info(request.key)
            try:
                start_nearest_city = closest_city(request.start)['city']
                end_nearest_city = closest_city(request.dest)['city']
                urls.append('http://' + urllib.quote('www.gobarnacle.com/request/from/' + start_nearest_city + '/to/' + end_nearest_city))
                urls.append('http://' + urllib.quote('www.gobarnacle.com/request/from/' + start_nearest_city))
                urls.append('http://' + urllib.quote('www.gobarnacle.com/request/to/' + end_nearest_city))
            except:
                logging.warn('error for request: ' + request.key)
        return set(urls)



class SitemapHandler(BaseHandler):
    """
    Sitemap for google to crawl urls for SEO
    """
    def get(self):
        self.response.headers['Content-Type'] = 'application/xml'
        self.write(Sitemap.retrieve_contents())

