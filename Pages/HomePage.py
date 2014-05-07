from Handlers.BaseHandler import *
from Utils.PageUtils import *
import urlparse
import json

class HomePage(BaseHandler):
    """ Home page, first page shown """
    def get(self):
        if self.user_prefs:
            #nr = Request.newest(5)
            #self.params['new_requests'] = [r.to_dict(incl_user=True) for r in nr]
            self.render('home.html', **self.params)
        else:
            referer = self.request.referer
            self.set_secure_cookie('referral', referer)
            self.render('landing/splash.html', **self.params)

class GuestPage(BaseHandler):
    """Guest Home page """
    def get(self):
        # nr = Request.newest(5)
        # self.params['new_requests'] = [r.to_dict(incl_user=True) for r in nr]
        self.render('home.html', **self.params)

class SplashPage(BaseHandler):
    """ About page """
    def get(self):
        self.render('landing/splash.html', **self.params)

class AboutPage(BaseHandler):
    """ About page """
    def get(self):
        self.render('about.html', **self.params)

class LocationPage(BaseHandler):
    """ About page """
    def get(self):
        self.render('location.html', **self.params)

class PrivacyPage(BaseHandler):
    """ Privacy page """
    def get(self):
        self.render('privacy.html', **self.params)

class PressPage(BaseHandler):
    """ Press page """
    def get(self):
        self.render('press.html', **self.params)

class HowItWorksPage(BaseHandler):
    """ How it works page """
    def get(self):
        self.render('how_it_works.html', **self.params)

class JobsPage(BaseHandler):
    """ Jobs page """
    def get(self):
        self.render('jobs.html', **self.params)


class TOSPage(BaseHandler):
    """ Terms of Service page """
    def get(self):
        self.render('tos.html', **self.params)

class Kickstarter(BaseHandler):
    """ Terms of Service page """
    def get(self):
        self.render('kick/index.html', **self.params)

class TrackerPage(BaseHandler):
    """ Terms of Service page """
    def get(self):
        self.render('track/tracker.html', **self.params)

class BlogPage(BaseHandler):
    def get(self, post=None):
        if not post:
            post = 'None'
        elif post[-4:]=='html':
            post = post[:-5]
        # cuz googlebot was appending .html to the urls
        self.params['blog_post'] = post
        self.render('/blog/'+post+'.html', **self.params)

class NavHelper(BaseHandler):
    """ Generating the header """
    def get(self):
        if self.user_prefs:
            header = gen_header(self.user_prefs)
        else:
            header = gen_header(None)
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(header))

