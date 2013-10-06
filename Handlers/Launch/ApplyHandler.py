from Handlers.BaseHandler import *
from Models.Launch.DriverModel import *
from Utils.ValidUtils import parse_date
import logging
import json

from google.appengine.api import mail

class ApplyHandler(BaseHandler):
    def get(self):
        self.render('launch/apply.html', **self.params)  
                    
    def post(self,action=None):
        if action=='fb':
            self.__fb()
        # firstname = self.request.get('firstname')
        # lastname = self.request.get('lastname')
        # email = self.request.get('email')
        # tel = self.request.get('tel')
        # loc = self.request.get('loc')
        # details = self.request.get('details')
        # freq = self.request.get('freq')
        # dist = self.request.get_all('dist')
        # remoteip = self.request.remote_addr
        #self.send_message(msg,subject,email,name,remoteip)        
        # self.write('ok')
    def __fb(self):
        d = json.loads(self.request.body)
        remoteip = self.request.remote_addr
        logging.info(d)   
        self.response.headers['Content-Type'] = "application/json"
        fb = d['fb']
        fbid = fb['id']
        # if not fbid:
            # response = { 'status': 'no'}        
            # self.write(json.dumps(response))             
            # return
        first_name = d['first_name']
        last_name = d['last_name']
        email = d['email']
        tel = d['tel']
        details = d['details']
        descr = d['descr']
        # save all fb info together
        # fbfname = fb['first_name']
        # fblname = fb['last_name']
        # fbemail = fb['email']
        # education = fb['education']
        # work = fb['work']
        # loc = fb['location']
        try:
            freq = int(d['freq'])
        except:
            freq = 0
        try:
            dist = [int(w) for w in d['dist']]
        except:
            dist = []
        dob = parse_date(fb['birthday'])
        try:
            dr = DriverModel( first_name = first_name, last_name = last_name, 
                email = email, freq = freq, dist = dist, dob = dob, 
                tel = tel, details = details, descr = descr, fb = fb, fbid = fbid)
#                fbfirstname = fbfname, fblastname = fblname, fbemail = fbemail, 
#                fbid = fbid, education = education, work = work, loc = loc)  
            dr.put()
            response = { 'status': 'new'}        
        except:
            response = {'status': 'err'}
        self.write(json.dumps(response))
        logging.info('Driver application submitted '+email) 
        #self.send_message('new driver',email,first_name+last_name,remoteip) 
        
    def send_message(self,msg,email,name,remoteip):
        if not name:
            name = "Barnacle"
        subject = "Feedback"
        text = u'From: %s (%s)' % (name, email)
        text += u'\n' + ('-' * len(text)) + '\n\n' + msg + '\n\n' + remoteip
        mail.send_mail('elaine.ou@gmail.com','elaine.ou@gmail.com', subject=subject, body=text)        