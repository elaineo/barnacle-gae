from Handlers.BaseHandler import *
from Models.ImageModel import *
from Models.User.Account import *
from Models.User.Driver import *
from Handlers.ImageHandler import *
from google.appengine.api import images
from google.appengine.api import users
import logging
import json

class DriverHandler(BaseHandler):
    def get(self, key=None):
        if not key:
            if not self.user_prefs:
                self.redirect('/#signin-box')
            else:
                self.__index()
        else:
            self.__public(key)          
        
    def __index(self):
        """ User profile information page """
        self.params['createorupdate'] = 'Ready to Drive'
        d = Driver.by_userkey(self.user_prefs.key)
        self.params['driver'] = True
        if d: #existing driver
            self.redirect('/route')
            return
        # else first time being driver
        self.params.update(self.user_prefs.params_fill())
        self.render('user/forms/filldriver.html', **self.params)
            
    def post(self,action=None):       
        if not self.user_prefs: # if user is not logged in, redirect to login page, which will redirect back
            self.redirect('/#signin-box')            
        if not action:
            self.__profile()
        elif action=='photo':
            self.__updateimg()
            
    def __updateimg(self):
        img = self.request.get("file")
        if img: 
            d = Driver.by_userkey(self.user_prefs.key)
            if d.img_id: # existing image
                imgstore = ImageStore.get_by_id(d.img_id)
                imgstore.update(img)
            else: # new image
                imgstore = ImageStore.new(img)
            imgstore.put()
            d.img_id = imgstore.key.id()
            d.put()
        self.response.headers['Content-Type'] = "application/json"
        response = {'status':'ok', 'img_url': d.vehicle_image_url()}
        self.write(json.dumps(response))
            
    def __profile(self):
        user_prefs = self.user_prefs
        user_prefs.first_name = self.request.get("first_name").capitalize()
        user_prefs.last_name = self.request.get("last_name")
        user_prefs.about = self.request.get("about").replace('\n','')

        # validate
        location = self.request.get("loc")
        if location:
            user_prefs.location = location
        lat = self.request.get('startlat')
        lon = self.request.get('startlon')
        if lat and lon:
            user_prefs.locpt = ndb.GeoPt(lat,lon)
        # image upload
        img = self.request.get("file")
        if img: 
            if user_prefs.img_id and user_prefs.img_id>=0: # existing image
                imgstore = ImageStore.get_by_id(user_prefs.img_id)
                imgstore.update(img)
            else: # new image
                imgstore = ImageStore.new(img)
            imgstore.put()
            user_prefs.img_id = imgstore.key.id()
        user_prefs.put()
        logging.info('User turns into a driver')
        self.redirect(user_prefs.profile_url())