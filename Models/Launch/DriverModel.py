from google.appengine.ext import ndb
import logging
import json
import urllib2

# Models #
##########
    
class DriverModel(ndb.Model):
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    tel = ndb.StringProperty()
    details = ndb.TextProperty()
    descr = ndb.StringProperty()
    freq = ndb.IntegerProperty()
    dist = ndb.IntegerProperty(repeated=True)
    fb = ndb.JsonProperty()
    fbfirst_name = ndb.StringProperty()
    fblast_name = ndb.StringProperty()
    fbemail = ndb.StringProperty()
    fbid = ndb.StringProperty(required=True)
    education = ndb.JsonProperty()
    work = ndb.JsonProperty()
    dob = ndb.DateProperty()
    loc = ndb.JsonProperty()
    creation_date = ndb.DateTimeProperty(auto_now_add=True)    
    
    @classmethod
    def by_id(cls, fb):
        u = cls.query(cls.fbid == fb)
        return u
        
    def profile_image_url(self, mode = None):
        # use FB picture
        fburl = 'http://graph.facebook.com/'+self.fbid+'/picture?redirect=false'
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