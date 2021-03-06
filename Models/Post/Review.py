from google.appengine.ext import ndb
import logging
import uuid
import json
import urllib2

""" Reviews are attached to Offers """

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
    def by_reservation(cls, rezkey, sender=None):
        if sender:
            r =  cls.query(cls.sender==sender, ancestor=rezkey)
            return r.get()
        else:
            return cls.query(ancestor=rezkey)
    @classmethod
    def sender_and_receiver(cls, sender, receiver):
        exist_r =  cls.query().filter(ndb.AND(cls.sender == sender, cls.receiver == receiver))
        return exist_r.get()
    @classmethod
    def avg_rating(cls, receiver):
        revs = cls.query(cls.receiver==receiver)
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
    def to_dict(self):
        d={ 'sender' : self.sender.urlsafe(),
            'receiver' : self.receiver.urlsafe(),
            'rating': self.rating,
            'content': self.content,
            'created': self.created.strftime('%Y-%b-%d') }
        d['sender_name'] = self.sender_name()
        d['review_thumb'] = self.review_thumb()
        return d