from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import taskqueue
from Handlers.Post.Post import PostHandler

from Models.Post.Post import PostStatus
from Models.Post.Request import *

from Utils.RouteUtils import RouteUtils
from Utils.SearchDocUtils import create_request_doc
from Utils.ValidUtils import *
import logging
import json
import time

class RequestHandler(PostHandler):
    """ Post a new route """
    def get(self, action=None,key=None):
        if not action and key:
            self.view_page(key)
            return
        if action=='json' and key:
            # dump route map
            try:
                route=ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            rdump = RouteUtils.dumppts([route.start,route.dest])
            self.response.headers['Content-Type'] = "application/json"
            self.write(rdump)
            return
        elif action=='updatecc' and key:
            reqs = Request.by_userkey(ndb.Key(urlsafe=key))
            for p in reqs:
                p.stats.status = RequestStatus.index('PURSUE')
                p.put()
            return
        if action and not self.user_prefs:
            self.redirect('/request#signin-box')
            return
        elif action=='repost' and key:
            try:
                p = ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            if p.key.parent() == self.user_prefs.key and p.dead>0:
                self.params.update(p.to_dict(True))
                self.params['route_title'] = 'Repost Delivery Request'
                self.params['delivby'] = ''
                self.render('post/forms/editrequest.html', **self.params)
                return
        elif action=='edit' and key:
            try:
                p = ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            if p.key.parent() == self.user_prefs.key:
                self.params.update(p.to_dict(True))
                self.params['route_title'] = 'Edit Delivery Request'
                self.render('post/forms/editrequest.html', **self.params)
                return
        elif not key:
            remoteip = self.request.remote_addr
            savsearch = SearchEntry.by_ip(remoteip)
            pop = self.request.get('pop')
            # create new request post
            if savsearch and bool(pop):
                self.params.update(savsearch.params_fill())
        self.params['route_title'] = 'Post a Delivery Request'
        self.params['today'] = datetime.now().strftime('%Y-%m-%d')
        self.render('post/forms/fillrequest.html', **self.params)

    def post(self, action=None,key=None):
        if action=='update' and key:
            self.__update_request(key)
        elif (action=='edit' or action=='repost') and key:
            try:
                p = ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return

            if not self.user_prefs:
                self.redirect('/request#signin-box')
                return
            if p.key.parent() == self.user_prefs.key:
                self.__edit_request(key)
                return
            logging.error(p)
            self.abort(403)
            return
        elif action=='delete' and key:
            self.delete(key)
        else:
            self.__init_request()


    def __edit_request(self,key=None):
        capacity = self.request.get('vcap')
        capacity = parse_unit(capacity)
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        items = self.request.get('items')
        reqdate = self.request.get('reqdate')
        img = self.request.get("file")
        if reqdate:
            delivby = parse_date(reqdate)
        else:
            delivby = datetime.now()+timedelta(weeks=1)

        start, startstr = self.__get_map_form('start')
        dest, deststr = self.__get_map_form('dest')
        logging.info('New Request: '+startstr+' to '+deststr)

        p = ndb.Key(urlsafe=key).get()
        if p and self.user_prefs and p.key.parent() == self.user_prefs.key:
            p.rates = rates
            p.details = items
            p.delivby = delivby
            p.locstart = startstr
            p.locend = deststr
            p.start = start
            p.dest = dest
            p.capacity=capacity
            # repost?
            if p.dead>0:
                logging.info('Request coming back from ' + PostStatus[p.dead])
                p.dead=0
                create_request_doc(p.key.urlsafe(), p)
            if img:
                if p.img_id: # existing image
                    imgstore = ImageStore.get_by_id(p.img_id)
                    imgstore.update(img)
                else: # new image
                    imgstore = ImageStore.new(img)
                imgstore.put()
                p.img_id = imgstore.key.id()
        else:
            self.redirect('/request')
        try:
            p.put()
            taskqueue.add(url='/match/updatereq/'+p.key.urlsafe(), method='get')
            taskqueue.add(url='/summary/selfnote/'+p.key.urlsafe(), method='get')
            create_request_doc(p.key.urlsafe(), p)
            fbshare = bool(self.request.get('fbshare'))
            self.params['share_onload'] = fbshare
            self.view_page(p.key.urlsafe())
        except:
            self.params['error_route'] = 'Invalid Locations'
            self.params['details'] = items
            self.params['capacity'] = capacity
            self.params['delivby'] = reqdate
            self.params['rates'] = rates
            self.params['route_title'] = 'Edit Delivery Request'
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('post/forms/fillrequest.html', **self.params)

    def __init_request(self,key=None):
        data = json.loads(unicode(self.request.body, errors='replace'))
        capacity = data.get('vcap')
        capacity = parse_unit(capacity)
        reqdate = data.get('reqdate')
        if reqdate:
            delivby = parse_date(reqdate)
        else:
            delivby = datetime.now()+timedelta(weeks=1)

        start, startstr = get_search_json(data,'start')
        dest, deststr = get_search_json(data,'dest')

        logging.info('Initial Request: '+startstr+' to '+deststr)
        distance = data.get('distance')
        p = Request(parent=self.user_prefs.key, start=start,
            dest=dest, capacity=capacity,
            delivby=delivby, locstart=startstr, locend=deststr)
        price, seed = RouteUtils.priceEst(p, distance)
        stats = ReqStats(sugg_price = price, seed = seed, distance = distance)
        p.rates = 0
        p.stats = stats

        try:
            p.put()
            self.params.update(p.to_dict(True))
            self.params['update_url'] = '/request/update/' + p.key.urlsafe()
            self.params['email'] = self.user_prefs.email
            if self.user_prefs.tel:
                self.params['tel'] = self.user_prefs.tel
            self.params['rates'] = price
            self.render('post/request_review.html', **self.params)
        except:  #this should never happen
            self.params['error_route'] = 'Invalid Locations'
            self.params['capacity'] = capacity
            self.params['delivby'] = reqdate
            self.params['route_title'] = 'Edit Delivery Request'
            self.params['today'] = datetime.now().strftime('%Y-%m-%d')
            self.render('post/forms/fillrequest.html', **self.params)

    def __update_request(self,key):
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        items = self.request.get('items')
        email = self.request.get('email')
        tel = self.request.get('tel')
        u = self.user_prefs.key.get()
        if email and (email != self.user_prefs.email):
            u.email = email
        if tel and (tel != self.user_prefs.tel):
            u.tel = tel
        u.put()
        p = ndb.Key(urlsafe=key).get()
        # image upload
        img = self.request.get("file")
        if p and self.user_prefs and p.key.parent() == self.user_prefs.key:
            if img:
                imgstore = ImageStore.new(img)
                imgstore.put()
                p.img_id = imgstore.key.id()
            p.rates = rates
            p.details = items
            p.stats.status = RequestStatus.index('PURSUE')
            p.put()
            logging.info('Complete request')
            logging.info(p)
            taskqueue.add(url='/match/updatereq/'+p.key.urlsafe(), method='get')
            taskqueue.add(url='/summary/selfnote/'+p.key.urlsafe(), method='get')
            taskqueue.add(url='/notify/thanks/'+p.key.urlsafe(), method='get')
            create_request_doc(p.key.urlsafe(), p)
            # If user already has cc on file, this is important.
            # else, collect a cc
            if not self.user_prefs.cc:
                p.stats.status = RequestStatus.index('NO_CC')
                logging.info(p)
                p.put()
                logging.info(p)
                self.params.update(self.user_prefs.params_fill())
                self.params['next_url'] = '/request/' + p.key.urlsafe()
                self.render('money/forms/cc.html', **self.params)
                return
            p.put()
            self.view_page(p.key.urlsafe())
        else:
            self.redirect('/request')

    def __get_map_form(self,pt):
        ptlat = self.request.get(pt+'lat')
        ptlon = self.request.get(pt+'lon')
        ptstr = self.request.get(pt+'str')
        if not ptstr or not ptlat or not ptlon:
            ptstr = self.request.get(pt)
            if ptstr:
                ptg = RouteUtils.getGeoLoc(ptstr)[0]
            else:
                ptg = None
        else:
            ptg = ndb.GeoPt(lat=ptlat,lon=ptlon)
        return ptg, ptstr
