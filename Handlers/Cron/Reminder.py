from Handlers.BaseHandler import BaseHandler
from Models.User.Account import UserPrefs
from Models.Post.Request import *
from Models.Post.OfferRequest import OfferRequest
from Models.Message import Message
from Utils.Email.Reminder import *
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
                    params = {'first_name': u.first_name, 'req_url': r.post_url()}
                    htmlbody =  self.render_str('email/reminders/complreq.html', **params)
                    textbody = complreq_txt % params 
                    sub = 'Reminder: Complete your delivery request'
                    send_info(u.email, sub, textbody, htmlbody)                    
                elif r.stats.status==RequestStatus.index('NO_CC'):
                    u = r.key.parent().get()
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
                sub = 'Reminder: Add a payment account'
                send_info(u.email, sub, textbody, htmlbody)