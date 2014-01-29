from Handlers.BaseHandler import *
from Models.MessageModel import *
from Utils.EmailUtils import create_msg
from Utils.Defs import post_msg_end
import json
import logging

class MessageHandler(BaseHandler):
    def get(self,action=None,key=None):
        if key and action=='route':
            self.__dumpmsgs(key)
        elif action=='box':
            self.__msgbox()
    def post(self,action=None,key=None):
        if not action:
            self.__newmsg()
        elif key and action=='route':
            self.__route(key)
        elif action=='send':
            self.__newmsg()
        elif action=='view':
            self.__view(key)            
    def __newmsg(self):
        # this is going to be handled by the front end unless they have a fake cookie
        if not self.user_prefs:
            self.redirect('/#signin-box')
        receiver = self.request.get('receiver')
        cc = bool(self.request.get('cc'))
        key = self.request.get('key')
        try:
            receiver = ndb.Key(urlsafe=receiver)
        except:
            self.abort(403)
            return            
        subject = self.request.get('subject')
        if len(subject) == 0:
            subject = '(no subject)'
        msg = self.request.get('msg')
        sender = self.user_prefs.key
        try: 
            #linked to a route
            url = ndb.Key(urlsafe=key).get()
            msg = msg + post_msg_end % key
        except:
            pass
        create_msg(self, sender, receiver, subject, msg)        
        if cc:  # cuz cc doesn't work. i'm too sick to figure it out.
            create_msg(self, sender, sender, subject, msg)
        recv = receiver.get()
        self.redirect(recv.profile_url() + '?msg=1')
        # response = { 'status': 'ok',
                    # 'next_url': recv.profile_url() + '?msg=1' }
        logging.info('New Message from ' + str(sender.id()) + ' to ' + str(receiver.id()))
        # self.response.headers['Content-Type'] = "application/json"
        # self.write(json.dumps(response))            

    def __route(self,key):
        #Message regarding a route
        # Scenarios:
        #   new msg from sender
        #   response from driver
        #   response from sender
        self.response.headers['Content-Type'] = "application/json"                
        data = json.loads(unicode(self.request.body, errors='replace'))
        logging.info(data)
        if not self.user_prefs:
            response = {'status':'Not logged in.'}
            self.write(json.dumps(response))
            return
        try:
            r = ndb.Key(urlsafe=key).get()
            receiver = ndb.Key(urlsafe=data.get('receiver'))
        except:
            response = {'status':'Invalid Route.'}
            self.write(json.dumps(response))
            return        
        msg = data.get('msg')   
        type = bool(data.get('type'))  #new stream (0) or response (1)
        m = Message(sender=self.user_prefs.key, msg=msg)
        if receiver == self.user_prefs.key: #responding to my own msg
            m.receiver=r.userkey
        else:
            m.receiver=receiver
        m.put()
        # does this stream already exist? check to make sure
        s = Stream.by_route_part(r.key,receiver)
        if not s:
            subject = r.locstart + ' to ' + r.locend
            s = Stream(routekey=r.key, participant=self.user_prefs.key, subject=subject)
            s.messages = [m.key]
        else:
            s.messages.append(m.key)
        s.put()
        response = {'status':'ok'}
        self.write(json.dumps(response))
        
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
    
    def __dumpmsgs(self,key):
        self.response.headers['Content-Type'] = "application/json"
        # streams sorted by date
        streams = Stream.by_routekey(ndb.Key(urlsafe=key))
        response = []        
        for s in streams:
            response.append(s.to_dict())
        self.write(json.dumps(response))
    
    def __view(self, key):
        m = ndb.Key(urlsafe=key).get()
        if m.receiver == self.user_prefs.key:
            m.mark_as_read()
            m.put()
        