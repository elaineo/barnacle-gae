import logging
from google.appengine.ext import ndb

from Handlers.BaseHandler import *
from Utils.FetchUtils import *

class ExternalHandler(BaseHandler):
    def get(self, action=None):
        if action=='zr':
            routes=fetch_routes('')
            logging.info(routes)

    def post(self, action=None):
        if action=='zr':
            url = self.request.get('url')
            routes = fetch_routes(url)