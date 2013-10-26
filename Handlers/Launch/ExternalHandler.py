from google.appengine.ext import ndb
from google.appengine.api import mail

from Handlers.BaseHandler import *

from Utils.Defs import www_home
from Utils.Defs import request_note_sub
from Utils.EmailUtils import send_info
from Utils.DefsEmail import *

class NotifyHandler(BaseHandler):
    def get(self, action=None):
        if action=='match2driver':
            self.__send_match2d()
        elif action=='match2sender':
            self.__send_match2s()
        else:
            return
                
    def __send_match2d(self):
        # Do some sort of search for each outstanding route lalala
        matches = []
        matches = [ndb.Key(urlsafe='agtzfnAycHBvc3RhbHIUCxIHUmVxdWVzdBiAgICA0LDtCww')]
        posts = []
        unroll=""
        for m in matches:
            p = m.get().to_search()
            if p['thumb_url'][0]=='/':
                p['thumb_url'] = www_home + p['thumb_url']                
            posts.append(p)
            unroll=unroll + "\n" + p['start'] + "\t" + p['dest'] + "\t" + p['delivby'] + "\t" + www_home + "/post/request/"+p['routekey']
        params = {'posts': posts}
        unrollparams = {'posts': unroll}
        self.send_match2d('elaine.ou@gmail.com', params, unrollparams)
        self.write(requestnote_txt % unrollparams)

    def __send_match2s(self):
        # Do some sort of search for each outstanding route lalala
        matches = []
        matches = [ndb.Key(urlsafe='agtzfnAycHBvc3RhbHISCxIFUm91dGUYgICAgJCGiQgM')]
        posts = []
        unroll=""
        for m in matches:
            p = m.get().to_search()
            if p['thumb_url'][0]=='/':
                p['thumb_url'] = www_home + p['thumb_url']                
            posts.append(p)
            unroll=unroll + "\n" + p['start'] + "\t" + p['dest'] + "\t" + p['delivend'] + "\t" + www_home + "/post/"+p['routekey']
        params = {'posts': posts}
        unrollparams = {'posts': unroll}
        self.send_match2s('joel@gobarnacle.com', params, unrollparams)
        
    def send_match2d(self, email, params, unrollparams):
        htmlbody =  self.render_str('email/requestnote.html', **params)
        textbody = requestnote_txt % unrollparams
        send_info(to_email=email, subject=request_note_sub, 
            body=textbody, html=htmlbody)
            
    def send_match2s(self, email, params, unrollparams):
        htmlbody =  self.render_str('email/routenote.html', **params)
        textbody = routenote_txt % unrollparams
        send_info(to_email=email, subject=request_note_sub, 
            body=textbody, html=htmlbody)            