import webapp2
import jinja2
import os
import logging
import urlparse
from google.appengine.api import users
from Utils.UserUtils import *
from Utils.FacebookUtils import login_url
from Models.User.Account import *
from Utils.PageUtils import *
from Utils.data.Defs import signin_reg, blank_img, signin_pattern

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
        # webapp2 does not handle utf-8json encoding from facebook
        if self.request.charset == 'utf-8json':
            self.request.charset = 'utf-8'
        self.params = {} # parameters to pass to template renderer
        self.set_current_user()
        self.fill_header()
        p = urlparse.urlparse(self.request.url)
        url = p.scheme + '://' + p.netloc + '/signup/fb'
        self.params['login_url'] = login_url(url)

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
            header = gen_header(None)
            p = urlparse.urlparse(self.request.url)
            redirect_uri = p.scheme + '://' + p.netloc + '/signup/fb'
            header['nickname'] = header['nickname'] % login_url(redirect_uri)
            self.params.update(header)
            # set referer cookie if not from Barnacle
            referer = self.request.referer
            if referer and referer[0:25].lower()!='http://www.gobarnacle.com/'[0:25]:
                self.set_secure_cookie('referral', referer)


def gen_header(up=None):
    header = {}
    header['nickname'] = signin_pattern
    if up:
        header['account_links'] = gen_account_links(up)
        header['nickname'] = up.nickname()
        header['prof_thumb'] = up.profile_image_url('small')
    else:
        header['prof_thumb'] = blank_img
    return header
