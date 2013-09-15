from google.appengine.api import mail

import logging
import re
from Models.UserModels import *
from Utils.Defs import noreply_email, email_domain, msg_start
from Utils.Defs import confirm_res_sub, info_email, bcc_email
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler

class EmailHandler(InboundMailHandler):
    def receive(self, mail_message):
        sender_email = extract_email(mail_message.sender)
        sender_email = encode_email_address(sender_email)
        
        to_email = extract_email(mail_message.to)        
        to_email = decode_email_address(to_email)
        logging.info("Received a message from: " + sender_email)
        logging.info("Received a message to: " + mail_message.to)        
        
        if not to_email:
            logging.error("couldn't find " + mail_message.to)
            return

        plaintext_bodies = mail_message.bodies('text/plain')
        plain_body = ''
        for content_type, body in plaintext_bodies:
            plain_body = plain_body + body.decode()
        
        send_mail(sender_email, to_email, mail_message.subject, plain_body)

def extract_email(email):
    buf = re.findall('<.+>',email)
    if len(buf) > 0:
        return buf[0][1:-1]
    else:
        return email
def encode_email_address(email):
    k = UserPrefs.by_email(email)
    if k is None:
        return 'Barnacle <' + email + '>'
    return k.first_name + ' via Barnacle <' + str(k.key.id()) + email_domain + '>'
def decode_email_address(email):
    buf = email.split('@')
    id = int(buf[0])
    k = ndb.Key('UserPrefs', id)
    up = k.get()
    if up is None:
        return 
    return up.email
        
def create_msg(sender, receiver, subject, msg):
    send_name = sender.get().first_name
    send_email = send_name + ' via Barnacle <' + str(sender.id()) + email_domain + '>'
    recv_email = str(receiver.id()) + email_domain
    body = (msg_start % send_name) + msg
    mail.send_mail(sender=send_email, 
                    to=recv_email, 
                    subject=subject, 
                    body=body)

def create_note(receiver, subject, body): 
    recv_email = str(receiver.id()) + email_domain
    mail.send_mail(sender=noreply_email,
                  to=recv_email,
                  subject=subject,
                  body=body)
    
def send_mail(sender_email, to_email, subject, body):
    mail.send_mail(sender=sender_email,
                  reply_to=sender_email,
                  to=to_email,
                  subject=subject,
                  body=body)
                  
def send_info(to_email, subject, body, html=None):
    if html:
        mail.send_mail(to=to_email, bcc=bcc_email,
            sender=info_email, subject=subject, 
            body=body, html=html)           
    else:
        mail.send_mail(to=to_email, bcc=bcc_email,
            sender=info_email, subject=subject, 
            body=body)           
        
        