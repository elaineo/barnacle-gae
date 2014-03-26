from Handlers.BaseHandler import *
from Models.User.Account import *
from Utils.ValidUtils import parse_date, get_search_json
import logging
import json
from Utils.data.Defs import CITY_DB_PATH, CITYV6_DB_PATH
import pygeoip

from google.appengine.api import mail

class ApplyHandler(BaseHandler):
    def get(self,action=None):
        if action=='nofb':
            self.render('user/nofb.html', **self.params)  
        else:
            self.render('user/apply.html', **self.params)  
                    
    def post(self,action=None):
        if action=='fb':
            self.__fb()
        elif action=='nofb':
            self.__nofb()
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
            dob = parse_date(fb['birthday'])        
            dist = [int(w) for w in d['dist']]
        except:
            dist = []
            dob = None
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

    def __nofb(self):
        d = json.loads(self.request.body)
        remoteip = self.request.remote_addr
        logging.info(d)   
        self.response.headers['Content-Type'] = "application/json"
        name = d.get('name')
        email = d.get('email')
        tel = d.get('tel')
        
        try:
            usertype = int(d.get('usertype'))
        except:
            usertype = 2
        
        start, startstr = get_search_json(d,'start')
        
        # lookup ip address
        gi = pygeoip.GeoIP(CITY_DB_PATH)
        geo = gi.record_by_addr(remoteip)    
        if not geo: 
            gi = pygeoip.GeoIP(CITYV6_DB_PATH)
            geo = gi.record_by_addr(remoteip)                
        if geo:
            geocity = geo.get('city') #hehehe
        else:
            geocity = ''   
        referral = self.read_secure_cookie('referral')
        code = self.read_secure_cookie('code')
        try:
            stats = UserStats(referral=referral, code=code, ip_addr=[remoteip], locations=[geocity])
        except:
            logging.info(geocity)
            stats = UserStats(referral=referral, code=code)            
                    
        try:
            dr = UserAccount( name = name, email = email, tel = tel, 
            locpt = start, location = startstr, stats = stats)
            dr.put()
            response = { 'status': 'new'}        
        except:
            response = {'status': 'err'}
        self.write(json.dumps(response))
        logging.info('Non-fb application submitted '+email)         