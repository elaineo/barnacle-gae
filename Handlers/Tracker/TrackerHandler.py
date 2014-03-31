import logging
import json
import urllib
from datetime import *
from google.appengine.ext import ndb
from datetime import *
import google.appengine.api.images
from Handlers.BaseHandler import *
from Models.Tracker.TrackerModel import *
from Models.Money.Transaction import *
from Utils.ValidUtils import parse_date, parse_bool
from Utils.ConfirmUtils import *
from Utils.EmailUtils import send_info
from Utils.Email.Track import sharetrack_txt
from Utils.data.EmailAddr import www_home
from Utils.RouteUtils import RouteUtils
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


# Image Uploading
# The blobstore uploading requires the construction of a url to be submitted as
# part of a multiform form. To be compatible with the iOS app, we need to return
# the upload url which the iOS can POST to. The iOS also needs be returned the
# url of the image
# 1) ask for upload url
# 2) post multiform to upload url
# 3) redirect to handler which returns a json response with image url
# 4) return image url in json
# ... then iOS posts image url with lat and long


class TrackerImageUploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('%s/tracker/image_upload/success/%s' % (www_home, blob_info.key()))


class TrackerImageUploadSuccess(BaseHandler):
    def get(self, blob_key):
        self.response.headers['Content-Type'] = "application/json"
        #url = images.get_serving_url(blobstore.BlobKey(blob_key))
        url = '%s/tracker/img/%s' % (www_home, blob_key)
        self.write(json.dumps({'url' : url}))


class TrackerImageUploadUrl(BaseHandler):
    def get(self):
        upload_url = blobstore.create_upload_url('/tracker/image_upload')
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps({'upload_url' : upload_url}))


class TrackerImageServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)


# Tracker Page


class TrackerHandler(BaseHandler):
    def get(self, action=None, key=None):
        if action=='update':
            # show active routes
            self.params['routes'] = self.__getroutes(0)
            self.render('track/web/update.html', **self.params)
        elif action=='create':
            self.render('track/web/create.html', **self.params)
        elif action=='manage':
            self.params['routes'] = self.__getroutes(None,True)
            self.params['completed'] = self.__getroutes(99)
            self.render('track/web/manage.html', **self.params)
        elif action=='confirm':
            # show active routes
            self.params['routes'] = self.__getroutes(0)
            self.render('track/web/confirm.html', **self.params)
        elif action=='share':
            self.render('track/web/share.html', **self.params)
        elif action=='getroutes':
            self.__dumproutes()
        elif action=='jsonroute' and key:
            try:
                route=ndb.Key(urlsafe=key).get()
            except:
                self.abort(400)
                return
            rdump = RouteUtils.dumptrack(route, [route.start,route.dest])
            self.response.headers['Content-Type'] = "application/json"
            self.write(rdump)
        elif action=='view' and key:
            self.__view_page(key,False)
        elif action=='mobile' and key:
            self.__view_page(key,True)
        elif action=='web':
            self.render('track/web/main.html', **self.params)

    def post(self, action=None, key=None):
        if action=='eta':
            self.__eta(key)
            return
        if not self.user_prefs:
            logging.error('Not logged in')
            response = { 'status': 'fail'}
            self.response.headers['Content-Type'] = "application/json"
            self.write(response)
            return
        if action=='updateloc':
            self.__updateloc()
        elif action=='create':
            self.__create()
        elif action=='status':
            self.__status()
        elif action=='msg':
            self.__sendmsg()
        elif action=='inactivate':
            self.__inactivate()
        elif action=='confirm':
            self.__confirm()
        elif action=='sendconfirm':
            self.__sendconfirm()
        elif action=='share':
            self.__share()
        else:
            return

    def __confirm(self):
        data = json.loads(self.request.body)
        logging.info(data)
        try:
            key = data['routekey']
            code = int(data['code'])
            r = ndb.Key(urlsafe=key).get()
            if not r:
                response = { 'status': 'Route not found.'}
            elif r.driver!=self.user_prefs.key:
                response = { 'status': 'Permission denied.'}
            else:
                if int(code)==pin_gen(r.key.id()):
                    r.status = 99
                    response = { 'status': 'ok'}
                    r.delivend = datetime.today()
                    r.put()
                else:
                    response = { 'status': 'Wrong code.'}
        except:
            response = { 'status': 'Failed.'}
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))


    def __status(self):
        data = json.loads(self.request.body)
        logging.info(data)
        try:
            key = data['routekey']
            status = int(data['status'])
            r = ndb.Key(urlsafe=key).get()
            if not r:
                response = { 'status': 'Route not found.'}
            elif r.driver!=self.user_prefs.key:
                response = { 'status': 'Permission denied.'}
            else:
                if status == 0: #delete
                    r.key.delete()
                else:
                    r.status = 1-r.status
                    r.put()
                response = { 'status': 'ok', 'newstat': r.status}
        except:
            response = { 'status': 'Failed.'}
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))

    def __inactivate(self):
        try:
            routes = TrackerModel.by_driver(self.user_prefs.key,0)  #only active ones
            for r in routes:
                r.status = 1
                r.put()
            response = { 'status': 'ok'}
        except:
            response = { 'status': 'Failed.'}
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))

    def __updateloc(self):
        #trackermodel
        data = json.loads(self.request.body)
        #logging.info(data)
        try:
            lat = float(data['lat'])
            lon = float(data['lon'])
            # todo: add speed
            loc =  ndb.GeoPt(lat=lat,lon=lon)
        except:
            loc = None
            response = { 'status': 'Failed.'}
        try:
            locstr = data['locstr']
        except:
            locstr = ''
        try:
            msg = data['msg']
            if msg[0:3].lower()=='http'[0:3]:
                msg='<a href="'+msg+'"><img style="max-height:60px" src="'+msg+'"></a>'
        except:
            msg = ''
        if loc:
            point = TrackPt(loc=loc, created=datetime.now(), locstr=locstr, msg=msg)
            routes = TrackerModel.by_driver(self.user_prefs.key,0)  #only active ones
            if routes.count(1)==0:
                response = { 'status': 'No active routes.'}
            else:
                for r in routes:
                    r.points.append(point)
                    r.put()
                response = { 'status': 'ok'}
        else:
            response = { 'status': 'Invalid location.'}
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))

    def __view_page(self,key,mobile=False):
        # try:
        p = ndb.Key(urlsafe=key).get()
        self.params.update(p.to_dict())
        self.params['first_name'] = p.driver.get().first_name
        if mobile:
            self.params['dispeta'] = False
            self.render('mobile/track.html', **self.params)
        else:
            self.render('track/track.html', **self.params)
        return
        # except:
            # self.abort(409)
            # return

    def __create(self):
        data = json.loads(self.request.body)
        logging.info(data)
        # try:
        tzoffset = int(data['tzoffset'])
        startlat = float(data['startlat'])
        startlon = float(data['startlon'])
        destlat = float(data['destlat'])
        destlon = float(data['destlon'])
        locstart = data['locstart']
        locend = data['locend']
        delivend = parse_date(data['delivend'])
        start = ndb.GeoPt(lat=startlat, lon=startlon)
        dest = ndb.GeoPt(lat=destlat, lon=destlon)
        response = { 'status': 'ok'}
        if start and dest:
            track = TrackerModel(driver = self.user_prefs.key, start = start,
                dest=dest, delivend=delivend, locstart=locstart, locend=locend,
                tzoffset=tzoffset)
            track.put()
            response['route'] = track.to_dict()
        # except:
            # response = { 'status': 'fail'}
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))

    def __dumproutes(self, status=None):
        if not self.user_prefs.key:
            response = { 'status': 'fail'}
        else:
            routes = self.__getroutes(status)
            response = { 'status': 'ok'}
            response['routes'] = routes
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))

    def __getroutes(self, status=None, comp=False):
        routes=[]
        if status is not None:
            tracks = TrackerModel.by_driver(self.user_prefs.key, status)
        elif comp:
            tracks = TrackerModel.by_driver(self.user_prefs.key, None, True)
        else:
            tracks = TrackerModel.by_driver(self.user_prefs.key)
        for t in tracks:
            routes.append(t.to_dict(True))
        return routes

    def __sendconfirm(self):
        data = json.loads(self.request.body)
        logging.info(data)
        try:
            key = data['routekey']
            r = ndb.Key(urlsafe=key).get()
            if not r:
                response = { 'status': 'Route not found.'}
            elif r.driver!=self.user_prefs.key:
                response = { 'status': 'Permission denied.'}
            elif not r.reservation: #No linked reservation
                response = { 'status': 'No recipients!'}
            else:
                response = { 'status': 'ok'}
                r.delivend = datetime.today()
                # change status to waiting
                r.status = 2
                r.put()
                #send a notification to the nonexistent customer
        except:
            response = { 'status': 'Failed.'}
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))

    def __share(self):
        data = json.loads(self.request.body)
        logging.info(data)
        fbshare = parse_bool(data.get('fbshare'))
        # try:
        key = data['routekey']
        r = ndb.Key(urlsafe=key).get()
        if not r:
            response = { 'status': 'Route not found.'}
        else:
            response = { 'status': 'ok'}
            self.params['share_onload'] = fbshare
            url = www_home + r.post_url()
            emails = data['emails']
            self.send_tracking(emails, url)
            response['route_url'] = r.mobile_url() + '?fbshare=1'
        # except:
            # response = { 'status': 'Failed.'}
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))

    def __sendmsg(self):
        data = json.loads(self.request.body)
        self.response.headers['Content-Type'] = "application/json"
        logging.info(data)
        key = data.get('routekey')
        msg = data.get('msg')
        if not self.user_prefs:
            response = {'status':'Not logged in.'}
            self.write(json.dumps(response))
            return
        try:
            r = ndb.Key(urlsafe=key).get()
            receiver = r.driver
        except:
            response = {'status':'Invalid Route.'}
            self.write(json.dumps(response))
            return

        sender = self.user_prefs.key
        if sender:
            point = TrackPt(sender=sender, created=datetime.now(), msg=msg)
            r.points.append(point)
            r.put()
            response = { 'status': 'ok'}

        self.write(json.dumps(response))

    def __eta(self, key):
        # this is probably the easiest way to do it. but i don't like it
        try:
            t = ndb.Key(urlsafe=key).get()
            eta = int(self.request.get('eta'))
        except:
            return
        response = {'status': 'ok'}
        if t.points:
            raweta = t.points[-1].created + t.tzdelta() + timedelta(0,eta)
            response['eta'] = raweta.strftime('%m/%d/%Y %H:%M')
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))


    def __debugcheckin(self):
        loc = ndb.GeoPt(lat=34, lon=-119.08)
        point = TrackPt(loc=loc, locstr='Bumfuck, CA', created=datetime.now(), msg='I just ran over a reindeer, i think i might need medical assistance, please send help')
        routes = TrackerModel.by_driver(self.user_prefs.key)
        for r in routes:
            r.points.append(point)
            r.put()
        return

    def send_tracking(self, emails, url):
        self.params['first_name'] = self.user_prefs.first_name
        self.params['url'] = url
        self.params['action'] = 'sharetracking'
        self.params['senderid'] = self.user_prefs.key.id()
        share_sub = self.params['first_name'] + " has shared a route with you"
        for email in emails:
            self.params['receiverid'] = email
            htmlbody =  self.render_str('email/sharetrack.html', **self.params)
            textbody = sharetrack_txt % self.params
            try:
                send_info(email, share_sub, textbody, htmlbody)
            except:
                continue

def create_from_res(r):
    tzoffset = RouteUtils.getTZ(r.dest)
    track = TrackerModel(start = r.start,
    dest=r.dest, delivend=r.deliverby, locstart=r.locstart,
    locend=r.locend, tzoffset=tzoffset, reservation=r.key)
    # create transaction as well
    track.driver = r.driver
    track.sender = r.sender
    track.put()
    trans = Transaction(parent=r.key, sender=track.sender, driver=track.driver)
    trans.put()
