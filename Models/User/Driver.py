from google.appengine.ext import ndb
import logging
import json
from Utils.data.Defs import ins_str, ins_str_email, bank_str
from Models.ImageModel import *
from Models.Post.Route import *

class Driver(ndb.Model):
    ins = ndb.BooleanProperty(default=False)
    bank = ndb.BooleanProperty(default=False)
    app_client = ndb.IntegerProperty()
    bank_acctnum = ndb.StringProperty()
    bank_name = ndb.StringProperty()
    bank_uri = ndb.StringProperty()
    makemodel = ndb.StringProperty()
    fb = ndb.JsonProperty()
    fbnetworks = ndb.StringProperty(repeated=True)   
    creation_date = ndb.DateTimeProperty(auto_now_add=True)    
    img_id = ndb.IntegerProperty()      

    def vehicle_image_url(self, mode = None):
        """ Retrieve link to profile thumbnail or default """
        if self.img_id:
            profile_image = ImageStore.get_by_id(self.img_id)
            if profile_image:
                buf = '/img/' + str(self.img_id) + '?key=' + profile_image.fakehash
                if mode:
                    buf += '&mode=' + mode
                return buf
        return '/static/img/placeholder_car.jpg'    
    
    def params_fill(self):
        params = {}
        params['bank'] = self.bank
        params['ins'] = self.ins
        params['driver'] = True
        params['vehicle_img'] = self.vehicle_image_url()
        if self.img_id:
            params['vehicle_img_ok'] = True
        if self.ins:
            params['insured'] = ins_str
            params['ins_email'] = ins_str_email
        else:
            params['insured'] = ''
            params['ins_email'] = ''  
        if self.bank:
            params['bankver'] = bank_str
        else:
            params['bankver'] = ''
        if self.fbnetworks:
            params['networks'] = self.fbnetworks
        else:
            params['networks'] = []
        if self.makemodel:
            params['makemodel'] = self.makemodel
        
        params.update(self.key.parent().get().params_fill())
        return params

    @classmethod
    def by_userkey(cls, key):
        u = cls.query(ancestor=key).get()
        return u        