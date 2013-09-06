import webapp2
import jinja2
import os
import logging
from google.appengine.api import users
from Models.UserUtils import *
from Models.UserModels import *
from Utils.PageUtils import *
from Utils.Defs import signin_reg, blank_img

jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader('templates'), autoescape = True)

class BaseHandler(webapp2.RequestHandler):
    """ BaseHandler, generic helper functions and user handling """
    current_user_key = None
    user_prefs = None # preferences for logged in user    
    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """ render jinja tempalte """
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        """ render and write """
        if len(kw) == 0:
            self.write(self.render_str(template, **self.params))
        else:
            self.write(self.render_str(template, **kw))

    def initialize(self, *a, **kw):
        """ called every time """
        webapp2.RequestHandler.initialize(self, *a, **kw) 
        self.params = {} # parameters to pass to template renderer
        self.set_current_user()
        self.fill_header()

    def set_secure_cookie(self, name, val):
        """ set cookie """
        cookie_val = make_secure_val(val)
        self.response.headers.add_header('Set-Cookie',
                '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        """ read cookie """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, email, acct=None):
        if not acct:
            self.set_secure_cookie('account', 'p2p')
            self.set_secure_cookie('user_id', str(email))
        elif acct:
            self.set_secure_cookie('account', acct)
            self.set_secure_cookie('user_id', str(email))
            
    def logout(self):
        """ logout by deleting cookie """
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')
        self.response.headers.add_header('Set-Cookie', 'account=; Path=/')

    def set_current_user(self):
        # check google account
        user = users.get_current_user()
        if user:
            up = UserPrefs.by_userid(user.user_id())
            if not up:
                up = UserPrefs(userid = user.user_id(), account_type = 'google')
                up.put()
            #set cookie
            logacct = self.read_secure_cookie('account')
            if logacct=='':
                self.set_secure_cookie('account', 'google')
                self.set_secure_cookie('user_id', str(up.userid))
            self.user_prefs = up
            self.current_user_key = up.key
        #otherwise it's a p2p account or facebook
        email = self.read_secure_cookie('user_id')
        if email:
            up = UserPrefs.by_userid(email)
            if up:            
                self.user_prefs = up
                self.current_user_key = up.key
        elif self.request.get('login_token'):
            user = UserAccounts.by_login_token(self.request.get('login_token'))
            if user:
                self.user_prefs = UserPrefs.by_email(user.email)
                self.current_user_key = self.user_prefs.key
                
    def fill_header(self):
        """ fill in header information params """
        if self.user_prefs:
            self.params.update(gen_header(self.user_prefs))
        else:
            self.params.update(gen_header(None))

def gen_header(up=None):
    header = {}
    header['nickname'] = signin_reg
    if up:
        header['account_links'] = gen_account_links(up)
        header['nickname'] = up.nickname()
        header['prof_thumb'] = up.profile_image_url('small')
    else:
        header['prof_thumb'] = blank_img
    return header            