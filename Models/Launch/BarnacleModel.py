from Models.ImageModel import *
from google.appengine.ext import ndb
import logging
import json
import urllib2

class BarnacleModel(ndb.Model):
    seed = ndb.IntegerProperty(default=10)
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    about = ndb.StringProperty()
    ins = ndb.BooleanProperty(default=False)
    completed = ndb.IntegerProperty(default=0)
    fb = ndb.JsonProperty()
    fbemail = ndb.StringProperty()
    fblocation = ndb.StringProperty()
    userid = ndb.StringProperty(default='219360')
    fbnetworks = ndb.StringProperty(repeated=True)
    img_id = ndb.IntegerProperty()      # set to -1 if using FB picture    
    creation_date = ndb.DateTimeProperty(auto_now_add=True)    
    
    def profile_image_url(self, mode = None):
        """ Retrieve link to profile thumbnail or default """
        if self.img_id>=0:
            profile_image = ImageStore.get_by_id(self.img_id)
            if profile_image:
                buf = '/img/' + str(self.img_id) + '?key=' + profile_image.fakehash
                if mode:
                    buf += '&mode=' + mode
                return buf
        elif self.img_id==-1 and self.userid:
            # use FB picture
            fburl = 'http://graph.facebook.com/'+self.userid+'/picture?redirect=false'
            if mode == 'small':
                fburl += '&width=100&height=100'
            else:
                fburl += '&width=720&height=720'
            try:
                fbdata = json.loads(urllib2.urlopen(fburl).read())
                if fbdata['data']:
                    return fbdata['data']['url']
            except:
                logging.error('FB server shat the bed')
        if mode == 'small':
            return '/static/img/profile_placeholder_small.jpg'
        else:
            return '/static/img/profile_placeholder.jpg'

    def profile_url(self):
        return '/profile/' + self.key.urlsafe()
    
    def deliveries_completed(self):
        return self.completed
    def params_fill(self, params):
        if self.first_name:
            params['first_name'] = self.first_name
        else:
            params['first_name'] = ''
        if self.last_name:
            params['last_name'] = self.last_name
        else: 
            params['last_name'] = ''
        if self.fblocation:
            params['location'] = self.fblocation
        else:
            params['location'] = 'Mountain View, California'
        if self.about:
            params['about'] = self.about
        else:
            params['about'] = ''
        if self.fbnetworks:
            params['networks'] = self.fbnetworks
        else:
            params['networks'] = []
        #if 0 in self.get_notify():
        params['msg_ok'] = True
        #else:
        #    params['msg_ok'] = False
        params['profile_full'] = self.profile_image_url()
        #params['review_url'] = '/review?receiver='+self.key.urlsafe()
        params['review_json'] = '/review/json/'+self.key.urlsafe()
        params['email'] = self.email
        params['created'] = str(self.creation_date)[0:16]
        params['deliv_completed'] = self.completed
        return params
    def params_fill_sm(self, params):
        if self.first_name:
            params['first_name'] = self.first_name
        else:
            params['first_name'] = 'Barnacle'  
        params['profile_thumb'] = self.profile_image_url(mode='small')   
        params['profile_url'] = self.profile_url()
        params['avg_rating'] = 5       
        params['fbid'] = self.userid
        return params        

    @classmethod
    def by_email(cls, email):
        u = cls.query().filter(cls.email == email).get()
        return u     