from Handlers.BaseHandler import BaseHandler
from Models.User.Account import UserPrefs
from Models.Post.Request import *
from Models.Post.OfferRequest import OfferRequest
from Models.Message import Message
from Utils.Email.Reminder import *
from Utils.Email.Post import *
from Utils.EmailUtils import send_info
from datetime import datetime, timedelta
from google.appengine.ext import ndb
import logging

class Reminder(BaseHandler):
    def awhile_ago(self):
        return datetime.now() - timedelta(hours=2)

    def get(self, action=None):
        if action=='incomp':
            reqs = Request.query(Request.dead==0, Request.created<self.awhile_ago())
            for r in reqs:
                if r.stats.status==RequestStatus.index('INCOMP'):
                    u = r.key.parent().get()
                    logging.info(r)
                    params = {'first_name': u.first_name, 'req_url': r.post_url()}
                    htmlbody =  self.render_str('email/reminders/complreq.html', **params)
                    textbody = complreq_txt % params 
                    sub = complreq_sub
                    send_info(u.email, sub, textbody, htmlbody)
                elif r.stats.status==RequestStatus.index('NO_CC'):
                    u = r.key.parent().get()
                    logging.info(r)
                    params = {'first_name': u.first_name}
                    htmlbody =  self.render_str('email/reminders/addcc.html', **params)
                    textbody = addcc_txt % params 
                    sub = 'Reminder: Add a payment account'
                    send_info(u.email, sub, textbody, htmlbody)
            # check for reservations without cc
            res = OfferRequest.query(OfferRequest.dead==0, OfferRequest.created<self.awhile_ago())
            for r in res:
                u = r.key.parent().get()
                if not u.cc:
                    params = {'first_name': u.first_name}
                    htmlbody =  self.render_str('email/reminders/addcc.html', **params)
                    textbody = addcc_txt % params 
                    sub = addcc_sub 
                    send_info(u.email, sub, textbody, htmlbody)
                
class Notify(BaseHandler):
    def get(self, action=None, key=None):
        if action=='thanks':
            r = ndb.Key(urlsafe=key).get()
            u = r.key.parent().get()
            if r.__class__.__name__ == 'Route':
                params = {'first_name': u.first_name, 'post_url': r.post_url()}
                htmlbody =  self.render_str('email/thanks_route.html', **params)
                textbody = thanksroute_txt % params 
                sub = thanksroute_sub 
                send_info(u.email, sub, textbody, htmlbody)                    
            else: 
                params = {'first_name': u.first_name, 'post_url': r.post_url()}
                htmlbody =  self.render_str('email/thanks_req.html', **params)
                textbody = thanksreq_txt % params 
                sub = thanksreq_sub
                send_info(u.email, sub, textbody, htmlbody)           
        elif action=='expire':
            r = ndb.Key(urlsafe=key).get()
            u = r.key.parent().get()
            params = {'first_name': u.first_name, 'repost_url': r.repost_url()}
            htmlbody =  self.render_str('email/expire_req.html', **params)
            textbody = expirereq_txt % params 
            sub = expirereq_sub
            send_info(u.email, sub, textbody, htmlbody)           