from google.appengine.ext import ndb
import logging
import json
from Utils.Defs import ins_str, ins_str_email, bank_str

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
        #params['deliv_completed'] = self.completed
        return params

    @classmethod
    def by_userkey(cls, key):
        u = cls.query().filter(cls.userkey == key).get()
        return u             