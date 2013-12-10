from google.appengine.api import mail

import logging
import re
from Handlers.BaseHandler import *
from Models.UserModels import *
from Utils.Defs import noreply_email, email_domain, msg_start
from Utils.Defs import confirm_res_sub, info_email, bcc_email, noreply_email
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        logging.info(mail_message.original)
        extr_email = extract_email(mail_message.sender)
        sender_email = encode_email_address(extr_email)

        to_email = extract_email(mail_message.to)
        to_email = decode_email_address(to_email)
        logging.info("Received a message from: " + sender_email)
        logging.info("Received a message to: " + mail_message.to)

        if not to_email:
            logging.error("couldn't find " + mail_message.to)
            return

        mail_message.sender = sender_email
        mail_message.to = to_email
        mail_message.bcc = bcc_email
        mail_message.reply_to = sender_email
        mail_message.send()

def extract_email(email):
    buf = re.findall('<.+>',email)
    if len(buf) > 0:
        return buf[0][1:-1]
    else:
        return email

def encode_email_address(email):
    # Patch for if already encoded.
    # I don't know why it does this and I am too sick to figure it out
    if email_domain in email:
        try:
            id = int(email.split('@')[0])
            k = UserPrefs.get_by_id(id)
        except ValueError:
            return 'Barnacle Notification <' + email + '>'
    else:
        k = UserPrefs.by_email(email)
    if k is None:  ##this is going to be an issue for ppl who don't have email addr
        logging.info("Not found: "+ email)
        return info_email
    return k.first_name + ' via Barnacle <' + str(k.key.id()) + email_domain + '>'

def decode_email_address(email):
    buf = email.split('@')
    id = int(buf[0])
    up = UserPrefs.get_by_id(id)
    if up is None:
        logging.error('Email address missing')
        logging.info(email)
        return bcc_email
    else:
        return up.email

def create_msg(self, sender, receiver, subject, msg):
    params = {}
    params['send_name'] = sender.get().first_name
    send_email = params['send_name'] + ' via Barnacle <' + str(sender.id()) + email_domain + '>'
    recv_email = str(receiver.id()) + email_domain
    body = (msg_start % params['send_name']) + msg
    params['msg'] = msg
    params['action'] = 'usermsg'
    params['senderid'] = sender.id()
    params['receiverid'] = receiver.id()
    html =  self.render_str('email/usermsg.html', **params)
    mail.send_mail(sender=send_email,
                    to=recv_email,
                    subject=subject,
                    body=body,html=html)
    params['receiverid'] = 'bcc'
    html =  self.render_str('email/usermsg.html', **params)                    
    mail.send_mail(sender=send_email, 
                    to=bcc_email,
                    subject=subject,
                    body=body,html=html)                    

def create_note(self, receiver, subject, body):
    params = {}
    params['msg'] = body
    params['action'] = 'note'
    params['senderid'] = 'barnacle'
    params['receiverid'] = receiver.id()
    recv_email = str(receiver.id()) + email_domain
    html = self.render_str('email/createnote.html', **params)
    mail.send_mail(sender=noreply_email, 
              to=recv_email,
              subject=subject,
              body=body, html=html)
    params['receiverid'] = 'x'              
    html = self.render_str('email/createnote.html', **params)
    mail.send_mail(sender=bcc_email,
              to=recv_email,
              subject=subject,
              body=body, html=html)    

def send_info(to_email, subject, body, html=None):
    if html:
        mail.send_mail(to=to_email, bcc=bcc_email,
            sender=info_email, subject=subject,
            body=body, html=html)
    else:
        mail.send_mail(to=to_email, bcc=bcc_email,
            sender=info_email, subject=subject,
            body=body)