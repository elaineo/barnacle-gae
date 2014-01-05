from google.appengine.ext import ndb
import logging
import json
from Utils.Defs import ins_str, ins_str_email, bank_str
from Models.UserModels import Review

class Driver(ndb.Model):
    userkey = ndb.KeyProperty(required=True)  # the user_pref it is connected to
    ins = ndb.BooleanProperty(default=False)
    bank = ndb.BooleanProperty(default=False)
    bank_acctnum = ndb.StringProperty()
    bank_name = ndb.StringProperty()
    bank_uri = ndb.StringProperty()
    fb = ndb.JsonProperty()
    fbnetworks = ndb.StringProperty(repeated=True)   
    creation_date = ndb.DateTimeProperty(auto_now_add=True)    
    
    def params_fill(self, params):
        params['driver'] = True
        params['bank'] = self.bank
        params['ins'] = self.ins
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
        
        u = self.userkey.get()
        params['first_name'] = u.first_name
        params['deliv_completed'] = u.deliveries_completed()
        params['profile_url'] = u.profile_url()
        params['profile_thumb'] = u.profile_image_url('small')
        params['fbid'] = u.userid
        params['key'] = self.userkey
        params['avg_rating'] = Review.avg_rating(self.userkey)
        params['location'] = u.location
        params['about'] = u.about
        return params

    @classmethod
    def by_userkey(cls, key):
        u = cls.query().filter(cls.userkey == key).get()
        return u             