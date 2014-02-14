from google.appengine.ext import ndb
import logging
import json
from Utils.Defs import ins_str, ins_str_email, bank_str
from Models.Post.Review import Review

class Driver(ndb.Model):
    ins = ndb.BooleanProperty(default=False)
    bank = ndb.BooleanProperty(default=False)
    bank_acctnum = ndb.StringProperty()
    bank_name = ndb.StringProperty()
    bank_uri = ndb.StringProperty()
    fb = ndb.JsonProperty()
    fbnetworks = ndb.StringProperty(repeated=True)   
    creation_date = ndb.DateTimeProperty(auto_now_add=True)    
    
    def params_fill(self):
        params = {}
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
        
        params.update(self.key.parent().get().params_fill())
        return params

    @classmethod
    def by_userkey(cls, key):
        u = cls.query(ancestor=key).get()
        return u        