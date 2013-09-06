from Handlers.BaseHandler import *
from Models.UserModels import *
from Utils.EmailUtils import create_note
from Utils.Defs import review_msg, review_sub
import json
import logging

class ReviewHandler(BaseHandler):
    def get(self,action=None,key=None):
        if action=='json':
            self.__json()
        else:
            self.__index()
    def __json(self):
        self.response.headers['Content-Type'] = "application/json"
        p=self.request.get('user')
        reviews = Review.by_receiver(ndb.Key(urlsafe=p))
        self.write(json.dumps([r.to_jdict() for r in reviews]))
    def __index(self):
        receiver = self.request.get('receiver')            
        if not self.user_prefs:
            self.redirect('/profile/'+receiver+'#signin-box')
            return
        if receiver == self.user_prefs.key.urlsafe():
            self.redirect('/account')
            return
        try:
            r = ndb.Key(urlsafe=receiver).get()
        except:
            self.abort(400)
            return              
        self.params['recv_name'] = r.first_name
        self.params['receiver'] = receiver
        self.render('review.html', **self.params)
    def post(self):
        receiver = self.request.get('receiver')
        ratingstr = self.request.get('rating')
        if ratingstr:
            rating = int(ratingstr)
        else: 
            rating = 1
        content = self.request.get('content')
        if not self.user_prefs:
            self.params['content'] = content
            self.params['receiver'] = receiver
            self.render('review.html#signin-box', **self.params)
        sender = self.user_prefs.key
        recv = ndb.Key(urlsafe=receiver)
        try:
            rr = recv.get()
        except:
            self.abort(403)
            return 
        # check for existing review
        r = Review.sender_and_receiver(sender, recv)
        if r:
            r.rating = rating
            r.content = content + '\n\n' + r.content
        else:
            r = Review(sender = sender, receiver = recv, rating = rating, content = content)
        r.put()
        #Notify and send message
        n = self.user_prefs.get_notify()
        if 2 in n:        
            msg = self.user_prefs.first_name + review_msg
            create_note(recv, review_sub, msg)
        self.redirect(rr.profile_url())