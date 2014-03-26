from google.appengine.ext import ndb

from Handlers.BaseHandler import *
from Models.Post.Route import *
from Models.Post.Request import *
from Models.Post.OfferRoute import *
from Models.Post.OfferRequest import *

import json
import logging

class DumpHandler(BaseHandler):
    def get(self, key=None):
        if not self.user_prefs.key:
            self.abort(403)
            return
        routedump = self.__routedump(self.user_prefs.key)
        reqdump = self.__reqdump(self.user_prefs.key)
        resdump = self.__resdump(self.user_prefs.key)
        offdump = self.__offdump(self.user_prefs.key)
        compdump = self.__compdump(self.user_prefs.key)
        if routedump:
            self.params['disproute'] = True
        else:
            self.params['disproute'] = False
        if reqdump:
            self.params['dispreq'] = True
        else:
            self.params['dispreq'] = False
        if resdump:
            self.params['dispres'] = True
        else:
            self.params['dispres'] = False
        if offdump:
            self.params['dispoff'] = True
        else:
            self.params['dispoff'] = False
        if compdump:
            self.params['dispcomp'] = True
        else:
            self.params['dispcomp'] = False
        self.params['routedump'] = routedump
        self.params['reqdump'] = reqdump
        self.params['resdump'] = resdump
        self.params['offdump'] = offdump
        self.params['compdump'] = compdump
        self.render('user/routes_reqs.html', **self.params)

    def __routedump(self, key):
        routedump = []
        routes = Route.by_userkey(key)
        for r in routes:
            dump = r.to_dict()
            resdump = []
            for q in OfferRequest.by_route(r.key):
                resdump.append(q.to_dict())
            dump['reservations'] = resdump
            routedump.append(dump)
        return routedump
    def __reqdump(self, key):
        reqdump = []
        requests = Request.by_userkey(key)
        for r in requests:
            dump = r.to_dict()
            offdump = []
            for q in OfferRoute.by_route(r.key):
                offdump.append(q.to_dict())
            dump['offers'] = offdump
            reqdump.append(dump)
        return reqdump
    def __resdump(self, key):
        resdump = []
        for q in OfferRequest.by_user(key):
            resdump.append(q.to_dict())
        # Also dump fixed-route things
        return resdump
    def __offdump(self, key):
        offdump = []
        for q in OfferRoute.by_user(key):
            offdump.append(q.to_dict())
        return offdump
    def __compdump(self, key):
        compdump = []
        for q in OfferRoute.by_user(key,1):
            compdump.append(q.to_dict())
        for q in OfferRequest.by_user(key,1):
            compdump.append(q.to_dict())
        return compdump

