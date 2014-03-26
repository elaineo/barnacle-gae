from Handlers.BaseHandler import *
import logging
import urllib2

from google.appengine.api import mail

class ContactPage(BaseHandler):
    """ Contact page """
    def get(self):
        self.render('contact.html', **self.params)

    def post(self):
        msg = self.request.get('message')
        subject = self.request.get('subject')
        email = self.request.get('email')
        name = self.request.get('name')
        remoteip = self.request.remote_addr
        self.send_message(msg,subject,email,name,remoteip)
        self.render('thanks.html')

    def send_message(self,msg,subject,email,name,remoteip):
        if not name:
            name = "Barnacle"
        if not subject:
            subject = "Feedback"
        text = u'From: %s (%s)' % (name, email)
        text += u'\n' + ('-' * len(text)) + '\n\n' + msg + '\n\n' + remoteip
        mail.send_mail('help@gobarnacle.com','help@gobarnacle.com', subject=subject, body=text)
        