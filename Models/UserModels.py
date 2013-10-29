from google.appengine.ext import ndb
from Models.UserUtils import *
from Models.ImageModel import *
from Models.ReservationModel import *
import logging
import uuid
import json
import urllib2

# Models #
##########
    
class UserAccounts(ndb.Model):
    """ non-google user database """    
    email = ndb.StringProperty(required = True)
    pwhash = ndb.TextProperty(required = True)
    login_token = ndb.StringProperty()      #for mobile devices
    
    @classmethod
    def by_email(cls, email):
        u = cls.query(cls.email == email)
        return u
    @classmethod
    def login(cls, email, pw):
        u = cls.by_email(email).get()
        if u and valid_pwhash(email, pw, u.pwhash):
            return u
    @classmethod
    def by_login_token(cls, token):
        return cls.query().filter(cls.login_token == token).get()
    def set_login_token(self):
        self.login_token = str(uuid.uuid4())
        self.put()
        return self.login_token        
    def as_json(self):
        up = UserPrefs.by_email(self.email)
        message = {
            'login_token' : self.login_token,
            'fullName': up.fullname(),
            'email': up.email,
            'ukey': up.key.urlsafe()
        }
        return message

class UserSettings(ndb.Model):
    """ 0.Messages 1.Reservation updates 2.Review notify 3.Matching Delivery requests    4. Newsletter """ 
    notify = ndb.IntegerProperty(repeated=True) 
    permission = ndb.IntegerProperty(default=0) 
    
class UserPrefs(ndb.Model):
    """ Individual User data fields """
    account_type = ndb.StringProperty(default='fb') #p2p or social network
    userid = ndb.StringProperty() # fb unique identifier
    email = ndb.StringProperty() 
    cust_id = ndb.StringProperty() # customer payment ID
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    zip = ndb.StringProperty()  #eventually kill this
    location = ndb.StringProperty()
    fblocation = ndb.StringProperty()    
    locpt = ndb.GeoPtProperty(default=ndb.GeoPt(37.4,-122))
    about = ndb.TextProperty()
    last_active = ndb.DateTimeProperty(auto_now=True)
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    img_id = ndb.IntegerProperty()      # set to -1 if using FB picture
    settings = ndb.StructuredProperty(UserSettings)
    @classmethod
    def by_email(cls, email):
        u = cls.query(cls.email == email)
        return u    
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
    
    def deliveries_completed(self):
        cnt = ExpiredReservation.deliveries_completed(self.key) + ExpiredOffer.deliveries_completed(self.key)
        return cnt
    def deliveries_sent(self):
        cnt = ExpiredReservation.deliveries_sent(self.key) + ExpiredOffer.deliveries_sent(self.key)
        return cnt
    def get_notify(self):
        if self.settings:
            return self.settings.notify
        else:
            return []

    def params_fill_sm(self, params):
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
    
    def params_fill(self, params):
        if self.first_name:
            params['first_name'] = self.first_name
        else:
            params['first_name'] = ''
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
        #if 0 in self.get_notify():
        params['msg_ok'] = True
        #else:
        #    params['msg_ok'] = False
        params['profile_full'] = self.profile_image_url()
        params['message_url'] = '/message?receiver='+self.key.urlsafe()
        params['review_url'] = '/review?receiver='+self.key.urlsafe()
        params['review_json'] = '/review/json?user='+self.key.urlsafe()
        params['email'] = self.email
        params['deliv_completed'] = self.deliveries_completed()+self.deliveries_sent()
        params['notify'] = {'notify' : self.get_notify() }
        params['profile_thumb'] = self.profile_image_url(mode='small')    
        return params
    @classmethod
    def by_userid(cls, email):
        q = cls.query(cls.userid == email).get()
        return q

    @classmethod
    def by_email(cls, email):
        u = cls.query().filter(cls.email == email).get()
        return u 
        
class Review(ndb.Model):
    """ Reviews about users """
    sender = ndb.KeyProperty()
    receiver = ndb.KeyProperty()
    rating = ndb.IntegerProperty()
    content = ndb.TextProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    @classmethod
    def newest(cls,num):
        return cls.query().order(-cls.created).fetch(num)    
    @classmethod
    def by_sender(cls, sender):
        return cls.query().filter(cls.sender == sender)
    @classmethod
    def by_receiver(cls, receiver):
        return cls.query().filter(cls.receiver==receiver).order(-cls.created)
    @classmethod
    def sender_and_receiver(cls, sender, receiver):
        exist_r =  cls.query().filter(ndb.AND(cls.sender == sender, cls.receiver == receiver))
        return exist_r.get()
    @classmethod
    def avg_rating(cls, receiver):
        revs = cls.query().filter(cls.receiver==receiver)
        s = sum(r.rating for r in revs)
        cnt = float(revs.count())
        if cnt > 0:
            return s/cnt
        else:
            return 0
    def sender_name(self):
        return self.sender.get().fullname()
    def review_thumb(self):
        """ Retrieve link to profile thumbnail or default """
        s = self.sender.get()
        return s.profile_image_url('small')
    def to_jdict(self):
        d={ 'sender' : self.sender.urlsafe(),
            'receiver' : self.receiver.urlsafe(),
            'rating': self.rating,
            'content': self.content,
            'created': self.created.strftime('%Y-%b-%d') }
        d['sender_name'] = self.sender_name()
        d['review_thumb'] = self.review_thumb()
        return d