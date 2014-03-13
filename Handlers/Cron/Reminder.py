from Handlers.BaseHandler import BaseHandler
from google.appengine.api import mail
from Models.User.Account import UserPrefs
from Models.Post.Route import Route
from Models.Post.Request import Request
from Models.Post.OfferRequest import OfferRequest
from Models.Message import Message
from Utils.DefsEmail import *
from Utils.EmailUtils import *
from datetime import datetime, timedelta
from google.appengine.ext import ndb

class Reminder(BaseHandler):
    def awhile_ago(self):
        return datetime.now() - timedelta(hours=2)

    def get(self, action=None):
        if action=='incomp':
            reqs = Request.query(Request.created > self.awhile_ago()).filter(Request.dead==0)
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