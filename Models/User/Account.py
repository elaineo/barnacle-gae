from google.appengine.ext import ndb
from Models.UserUtils import *
from Models.Post.Review import Review
from Models.ImageModel import *
from Models.Money.Transaction import *
import logging
import uuid
import json
import urllib2

# Models #
##########
    
class UserStats(ndb.Model):
    referral = ndb.StringProperty()
    code = ndb.StringProperty()
    ip_addr = ndb.StringProperty(repeated=True)
    locations = ndb.StringProperty(repeated=True)
    
class UserSettings(ndb.Model):
    """ 0.Messages 1.Reservation updates 2.Review notify 3.Matching Delivery requests    4. Newsletter """ 
    notify = ndb.IntegerProperty(repeated=True) 
    
class UserPrefs(ndb.Model):
    """ Individual User data fields """
    account_type = ndb.StringProperty(default='fb') #p2p or social network
    userid = ndb.StringProperty() # fb unique identifier
    email = ndb.StringProperty() 
    tel = ndb.StringProperty() 
    cust_id = ndb.StringProperty() # customer payment ID
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    location = ndb.StringProperty()
    fblocation = ndb.StringProperty()    
    locpt = ndb.GeoPtProperty(default=ndb.GeoPt(37.4,-122))
    about = ndb.TextProperty()
    last_active = ndb.DateTimeProperty(auto_now=True)
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    img_id = ndb.IntegerProperty()      # set to -1 if using FB picture
    settings = ndb.StructuredProperty(UserSettings)
    stats = ndb.StructuredProperty(UserStats) 
    def fullname(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return "Barnacle"
    def nickname(self):
        if self.first_name and len(self.first_name) > 0:
            return self.first_name
        else:
            return 'Barnacle'
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
    
    def get_notify(self):
        if self.settings:
            return self.settings.notify
        else:
            return []

    def params_fill_sm(self):
        params = {}
        if self.first_name:
            params['first_name'] = self.first_name
        else:
            params['first_name'] = 'Barnacle'  
        params['profile_thumb'] = self.profile_image_url(mode='small')   
        params['profile_url'] = self.profile_url()
        params['avg_rating'] = Review.avg_rating(self.key)
        if params['avg_rating'] < 1:
            params['avg_rating'] = 5        
        params['fbid'] = self.userid
        return params
    
    def params_fill(self):
        params = self.params_fill_sm()
        if self.last_name:
            params['last_name'] = self.last_name
        else: 
            params['last_name'] = ''
        if self.location:
            params['location'] = self.location
        else:
            params['location'] = 'Mountain View, CA'
        if self.about:
            params['about'] = self.about
        else:
            params['about'] = ''
        if self.email:
            params['email'] = self.email
        else:
            params['email'] = ''
        params['profile_full'] = self.profile_image_url()
        params['review_json'] = '/review/json/'+self.key.urlsafe()
        params['email'] = self.email
        params['deliv_completed'] = Transaction.deliveries_completed(self.key)
        params['notify'] = {'notify' : self.get_notify() }
        return params
        
    @classmethod
    def by_userid(cls, email):
        q = cls.query(cls.userid == email).get()
        return q

    @classmethod
    def by_email(cls, email):
        u = cls.query(cls.email == email).get()
        return u        
    