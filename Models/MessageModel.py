import json
from google.appengine.ext import ndb
from Models.UserModels import *

class Stream(ndb.Model):
    routekey = ndb.KeyProperty(required=True)  #all msgs associated with a routekey
    subject = ndb.StringProperty(default='(no subject)')
    messages = ndb.KeyProperty(repeated=True)
    participant = ndb.KeyProperty(required=True)
    last_active = ndb.DateTimeProperty(auto_now=True)
    @classmethod
    def by_routekey(cls, key):
        return cls.query(cls.routekey==key).order(-cls.last_active)
    @classmethod
    def by_route_part(cls, routekey, pkey):
        return cls.query(ndb.AND(cls.routekey==routekey, cls.participant==pkey)).get()
    def to_dict(cls):
        s = { 'sender' : cls.participant.urlsafe(),
                'msgs' : [m.get().to_dict_min() for m in cls.messages] }
                #.sort(key=lambda x: x.created)
        return s
        
        
class Message(ndb.Model):    
    sender = ndb.KeyProperty()
    receiver = ndb.KeyProperty()
    msg = ndb.TextProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    unread = ndb.BooleanProperty(default=True)
    @classmethod
    def by_sender(cls, sender):
        return cls.query().filter(cls.sender==sender)
    @classmethod
    def by_receiver(cls, receiver):
        return cls.query().filter(cls.receiver==receiver).order(-cls.created)
    def sender_name(self):
        return self.sender.get().first_name
    def get_profile_url(self):
        return self.sender.get().profile_url()
    def receiver_userid(self):
        return self.receiver.get().userid
    def sender_userid(self):
        return self.sender.get().userid
    def get_reply_url(self):
        return '/message/view/' + str(self.key.urlsafe())
    def mark_as_read(self):
        self.unread = False
        self.put()        
    def to_dict(self):
        d={}
        d['msg']=self.msg
        d['created'] = self.created.strftime('%Y-%b-%d %X')
        d['unread']=self.unread
        d['sender_name'] = self.sender_name()
        d['prof_url'] = self.get_profile_url()
        d['reply_url'] = self.get_reply_url()
        d['sender'] = self.sender.urlsafe()
        d['receiver']=self.receiver.urlsafe()
        d['recv_id']=self.receiver_userid()
        d['send_id']=self.sender_userid()
        return d
        
    def to_dict_min(self):
        d={}
        d['sender_thumb']=self.sender.get().profile_image_url('small')
        d['sender_prof_url']=self.get_profile_url()
        d['sender']=self.sender_name()
        d['msg']=self.msg
        d['created'] = self.created.strftime('%Y-%b-%d %X')
        return d