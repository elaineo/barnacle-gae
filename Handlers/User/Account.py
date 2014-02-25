from Handlers.BaseHandler import *
from Models.User.Account import *
from Models.UserUtils import *
from Utils.Defs import CITY_DB_PATH, CITYV6_DB_PATH
import hashlib
import logging
import json
import pygeoip

class SignupPage(BaseHandler):
    """ User sign up page """
    def get(self):
        # we should never end up here.
        if self.user_prefs: # if user is logged in, redirect to profile
            self.redirect("/profile")
        else:
            self.redirect('/')

    def post(self,action=None):
        if not action:
            self.__post()
        elif action=='mobile':
            self.__mobile()
        elif action=='fb':
            self.__fb()

    def __post(self):
        # retrieve information
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        response = {}
        response['has_error'] = 0
        if not valid_email(email):
            response['erroremail']="That's not a valid email address."
            response['has_error'] = "email"
        else:
            response['email'] = email
        if UserAccounts.by_email(email).get():
            response['erroremail']="That user exists already."
            response['has_error'] = "email"
        if not valid_pw(password):
            response['errorpw0'] = "That wasn't a valid password."
            response['has_error'] = "password"
        elif password != verify:
            response['errorpw1'] = "Your passwords didn't match."
            response['has_error'] = "verify"
        if response['has_error']==0:
            # make user account
            u = UserAccounts(email = email, pwhash = make_pw_hash(email, password))
            u.put()
            up = UserPrefs(account_type = 'p2p', email = email, userid = email)
            up.put()
            # set cookies
            self.login(email)
            self.set_current_user()
            self.fill_header()
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))
    def __fb(self):
        # retrieve information
        # Fix for Bad content type: '; charset=utf-8'        
        if len(self.request.content_type) == 0:
            fp = self.request.environ['webob._body_file'][1]
            fp.reset()
            buf = fp.read()
            data = json.loads(buf)
        else:
            data = json.loads(unicode(self.request.body, errors='replace'))
        logging.info(data)
        remoteip = self.request.remote_addr
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        fbid = data.get('id')       
        email = data.get('email')
        if not email:
            username = data.get('username')
            if not username:
                username = fbid
            email = username+'@facebook.com'                
        try:
            location = data['location']['name']
        except:
            location = 'Mountain View, CA'
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
        # I guess we can assume there won't be an error for now
        if not fbid:
            response = { 'status': 'fail'}
        else:
            # make user account
            up = UserPrefs.by_userid(fbid)
            if not up:
                referral = self.read_secure_cookie('referral')
                code = self.read_secure_cookie('code')
                try:
                    stats = UserStats(referral=referral, code=code, ip_addr=[remoteip], locations=[geocity])
                except:
                    logging.info(geocity)
                    stats = UserStats(referral=referral, code=code)
                sett = UserSettings(notify=[1,2,3,4])
                up = UserPrefs(account_type = 'fb', email = email, userid = fbid, first_name = first_name, last_name = last_name, img_id = -1, settings=sett, location = location, fblocation = location, 
                stats=stats)
                up.put()
                self.user_prefs = up
                self.current_user_key = up.key
                response = { 'status': 'new'}
                logging.info('New account')
            else:
                response = { 'status': 'existing'}
                logging.info('Existing account login from ' + (geocity if geocity else ''))
                try:
                    if not up.stats and remoteip:
                        up.stats = UserStats(ip_addr=[remoteip], locations=[geocity])
                    elif remoteip not in up.stats.ip_addr:
                        up.stats.ip_addr.append(remoteip)
                    if geocity not in up.stats.locations:
                        up.stats.locations.append(geocity)
                    up.put()
                except:
                    logging.info(geocity)
                    logging.info(remoteip)
            # set cookies
            self.login(fbid, 'fb')
            self.set_current_user()
            self.fill_header()
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))

    def __mobile(self):
        self.response.headers['Content-Type'] = "application/json"
        # retrieve information
        password = self.request.get('password')
        email = self.request.get('email')
        name = self.request.get('name').split()
        mm={'error':None, 'name':name}
        if not valid_email(email):
            mm['error']="That's not a valid email address."
        else:
            mm['email'] = email
        if UserAccounts.by_email(email).get():
            mm['error']="That user exists already."
        if not valid_pw(password):
            mm['error'] = "That wasn't a valid password."
        if mm['error'] is not None:
            mm['status'] = 'error'
            self.write(json.dumps(mm))
            return
        else:
            # make user account
            u = UserAccounts(email = email, pwhash = make_pw_hash(email, password))
            u.put()
            up = UserPrefs(account_type = 'p2p', email = email)
            if name:
                up.first_name=name[0]
                up.last_name=name[-1]
            up.put()
            u.set_login_token()
            mm = u.as_json()
            mm['status'] = 'success'
            self.write(json.dumps(mm))
            return

class SigninPage(BaseHandler):
    """ User Sign In Page """
    def get(self):
        # we should never end up here
        self.redirect('/')
    def post(self,action=None):
        email = self.request.get('email')
        password = self.request.get('password')
        if not action:
            self.__post(email,password)
        elif action=='mobile':
            self.__mobile(email,password)
    def __post(self,email,password):
        u = UserAccounts.login(email, password)
        response = {}
        if u:
            self.login(email)
            self.set_current_user()
            self.fill_header()
            response['has_error'] = 0
        else:
            response['has_error'] = 'email'
            response['erroremail'] = 'invalid login'
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))
    def __mobile(self,email,password):
        self.response.headers['Content-Type'] = "application/json"
        if email and password:
            u = UserAccounts.login(email, password)
            if u:
                if not u.login_token:
                    u.set_login_token()
                mm = u.as_json()
                mm['status'] = 'success'
                self.write(json.dumps(mm))
                return
        mm = {'status' : 'fail'}
        self.write(json.dumps(mm))
        return


class SignoutPage(BaseHandler):
    """ User Sign Out Page """
    def get(self):
        logging.info('Log out')
        self.logout() # deletes cookie
        self.redirect('/')