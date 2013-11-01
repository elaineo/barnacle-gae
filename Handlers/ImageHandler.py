from Handlers.BaseHandler import *
from Models.ImageModel import *
from google.appengine.api import images
import os
import logging

class ImagePage(BaseHandler):
    """ handles images """
    def get(self, id):
        img = ImageStore.get_by_id(int(id))
        mode = self.request.get("mode")
        fakehash = self.request.get("key")
        if img and img.fakehash == fakehash:  # pass hash test to prevent scrapping     
            self.response.headers['Content-Type'] = "image/png"
            # return original / medium / small
            if mode == '': 
                self.write(img.image_medium)
            elif mode == 'original':
                self.write(img.image_orig)
            elif mode == 'small':
                self.write(img.image_small)
            else:
                self.write(img.image_small)
        else:
            self.error(404)

class ImageHandler(BaseHandler):
    def get(self, action=None, key=None):  
        if action=='blank':
            self.render('forms/filldriver.html', **self.params)
            return
        self.response.headers['Content-Type'] = "image/png"
        img = ImageStore.get_by_id(4811188005240832)
        self.write(img.image_small)
    def post(self, action=None, key=None):  
        if action=='blank':
            img = self.request.get("file")
            if img: 
                imgstore = ImageStore.new(img)
                imgstore.put()
                logging.info(imgstore.key.id())
                logging.info(imgstore.key.urlsafe())