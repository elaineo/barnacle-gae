from Handlers.BaseHandler import *
from Models.MessageModel import *
from Utils.EmailUtils import create_msg
import json
import logging

class MessageHandler(BaseHandler):
    def get(self,action=None):
        if not action:
            self.__blank()
        elif action=='box':
            self.__msgbox()
        elif action=='json':
            self.__msgjson()
    def post(self,action=None,key=None):
        if not action:
            self.__newmsg()
        elif action=='send':
            self.__newmsg()
        elif action=='view':
            self.__view(key)            
    def __newmsg(self):
        # this is going to be handled by the front end unless they have a fake cookie
        if not self.user_prefs:
            self.redirect('/#signin-box')
        receiver = self.request.get('receiver')
        if not receiver:
            self.abort(403)
            return
        receiver = ndb.Key(urlsafe=receiver)
        subject = self.request.get('subject')
        if len(subject) == 0:
            subject = '(no subject)'
        msg = self.request.get('msg')
        sender = self.user_prefs.key
        create_msg(sender, receiver, subject, msg)
        recv = receiver.get()
        response = { 'status': 'ok',
                    'next_url': recv.profile_url() + '?msg=1' }
        logging.info('New Message from ' + sender.urlsafe() + ' to ' + receiver.urlsafe())
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))            

    def __blank(self):
        receiver = self.request.get('receiver')
        subject = self.request.get('subject')
        msg = self.request.get('msg')
        response = {}
        self.params['recv_name'] = ndb.Key(urlsafe=receiver).get().first_name
        self.params['receiver'] = receiver
        self.params['subject'] = subject
        self.render('message.html', **self.params)
        
    def __msgbox(self):
        if not self.user_prefs:
            self.redirect('/#signin-box')
            return
        q = Message.by_receiver(self.user_prefs.key)
        msgs = []
        for msg in q:
            m={ 'sender': msg.sender_name(),
                'url': '/message/' + str(msg.key) }
            msgs.append(m)
        self.params['msgs'] = msgs
        self.render('message_box.html', **self.params)
    
    def __msgjson(self):
        self.response.headers['Content-Type'] = "application/json"
        msgs = Message.by_receiver(self.user_prefs.key)
        self.write(json.dumps([m.to_jdict() for m in msgs]))
    
    def __view(self, key):
        m = ndb.Key(urlsafe=key).get()
        if m.receiver == self.user_prefs.key:
            m.mark_as_read()
            m.put()
        