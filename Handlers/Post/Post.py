from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from Handlers.BaseHandler import *
from Models.Post.Post import PostStatus
from Models.Post.OfferRoute import OfferRoute
from Models.Post.OfferRequest import OfferRequest

from Utils.SearchDocUtils import delete_doc
import logging
import json

class PostHandler(BaseHandler):
    """ Post a new route or request """

    def delete(self, key=None):
        if key and self.user_prefs:
            r = ndb.Key(urlsafe=key).get()
            if r and r.key.parent()==self.user_prefs.key:
                # check to make sure nothing was confirmed
                # delete associated reservations
                type = r.__class__.__name__
                if r.num_confirmed() > 0:
                    return
                for q in r.offers:
                    route = q.get()
                    route.dead = PostStatus.index('DELETED')
                    route.put()
                if type=='Route':
                    if r.roundtrip:
                        delete_doc(r.key.urlsafe()+'_RT',type)
                # delete from matches
                taskqueue.add(url='/match/cleanmatch/'+key, method='get')
                # delete in search docs
                delete_doc(r.key.urlsafe(),type)
                r.dead = PostStatus.index('DELETED')
                r.put()
                self.redirect('/account')
            else:
                self.abort(403)
                return

    def view_page(self,keyrt):
        if keyrt.endswith('_RT'):
            key = keyrt[:-3]
        else:
            key = keyrt
        p = ndb.Key(urlsafe=key).get()
        if p:
            if p.dead > 0:
                self.view_dead(p)
                return
            p.increment_views()
            if self.user_prefs and self.user_prefs.key == p.key.parent():
                self.params['edit_allow'] = True
                if p.num_confirmed > 0:
                    self.params['resdump'] = route_resdump(p.key, p.__class__.__name__)
                if len(p.matches) > 0:
                    self.params['matchdump'] = route_matchdump(p)
            else:
                self.params['edit_allow'] = False
            if self.user_prefs and self.user_prefs.account_type == 'fb':
                self.params['fb_share'] = True
            self.params.update(p.to_dict(True))
            if p.__class__.__name__ == 'Route':
                self.render('post/post.html', **self.params)
            else:
                self.render('post/request.html', **self.params)
        else:
            self.abort(409)
        return

    def view_dead(self,route):
        self.params.update(route.to_dict(True))
        if route.__class__.__name__ == 'Route':
            self.render('landing/exppost.html', **self.params)
        else:
            self.render('landing/exprequest.html', **self.params)
        return
        

def route_resdump(key, name):
    resdump = []
    if name=='Route':
        for q in OfferRequest.by_route(key):
            resdump.append(q.to_dict())
    elif name=='Request':
        for q in OfferRoute.by_route(key):
            resdump.append(q.to_dict())
    return resdump

def route_matchdump(route):
    resdump = []
    for q in route.matches:
        k = q.get()
        if k:
            resdump.append(k.to_dict())
    return resdump        