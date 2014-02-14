from Handlers.BaseHandler import *
from Models.ImageModel import *
from Models.User.Account import *
from Models.Post.Route import *
from Models.Post.Request import *
from Models.Message import *
from Models.User.Driver import *
from Handlers.ImageHandler import *
from google.appengine.api import images
from google.appengine.api import users
from Utils.DefsEmail import welcome_txt
from Utils.Defs import welcome_sub
from Utils.EmailUtils import send_info
from Models.Post.Review import *
import logging

class ProfileHandler(BaseHandler):
    def get(self, key=None, action=None):
        if not key and not action:
            self.__index()
        elif action=='drivestart':
            self.render('user/drivestart.html',**self.params)
            return
        elif action=='drive':
            self.__index()
        else:
            self.__public(key)
          
        
    def __index(self):
        """ User profile information page """
        self.params['createorupdate'] = 'Create Profile'
        if not self.user_prefs: # bandaid -- for some reason it can't process initial login
            self.set_current_user()
            self.fill_header()
        else:
            self.params.update(self.user_prefs.params_fill())
            self.params['createorupdate'] = 'Update Profile'
        self.render('user/forms/fillprofile.html', **self.params)
    
    def __public(self,key):
        """ Public viewable profile """
        userprefs = ndb.Key(urlsafe=key).get()
        ms = self.request.get("msg")
        if ms:
            m = int(ms)
        else:
            m = 0
        if userprefs:
            self.params.update(userprefs.params_fill())
            self.params.update(fill_prof_stub_params(userprefs.key))            
            self.params['fbfriend'] = False
            self.params['m'] =m
            if self.user_prefs:
                self.params['fbaccount'] = True
                if self.user_prefs.key != userprefs.key:
                    self.params['fbfriend'] = True
                    self.params['fbid'] = userprefs.userid
            self.render('user/profile.html',**self.params)
        else:
            self.abort(400)
            return  
            
    def post(self, action=None):       
        if not self.user_prefs:
            #redirect to login page, which will redirect back
            self.redirect('/#signin-box')
            return
        if action == 'drive':
            self.__driverprofile()
        else:
            self.user_prefs = self.__profile()
            self.user_prefs.put()
            self.redirect(self.user_prefs.profile_url())

    def __driverprofile(self):
        notify = self.request.get_all('notify')
        email = self.request.get('email')
        self.user_prefs = self.__profile()
        if not notify:
            self.user_prefs.settings = UserSettings(notify = [])        
        else:
            self.user_prefs.settings = UserSettings(notify = [int(n) for n in notify])
        if email: 
            self.user_prefs.email = email
        self.user_prefs.put()
        d = Driver.by_userkey(self.user_prefs.key)
        if not d:
            d = Driver(parent=self.user_prefs.key)
            d.put()
            #new driver, send email
            logging.info('New driver :' + email)
            self.send_driver_info(email)
            self.render('user/drivestart.html',**self.params)
        else:            
            self.redirect('/post')
        
        
    def __profile(self):
        user_prefs = self.user_prefs
        user_prefs.first_name = self.request.get("first_name").capitalize()
        user_prefs.last_name = self.request.get("last_name")
        user_prefs.about = self.request.get("about").replace('\n','')

        # validate
        location = self.request.get("loc")
        if location:
            user_prefs.location = location
        lat = self.request.get('startlat')
        lon = self.request.get('startlon')
        if lat and lon:
            user_prefs.locpt = ndb.GeoPt(lat,lon)
        # image upload
        img = self.request.get("file")
        if img: 
            if user_prefs.img_id and user_prefs.img_id>=0: # existing image
                imgstore = ImageStore.get_by_id(user_prefs.img_id)
                imgstore.update(img)
            else: # new image
                imgstore = ImageStore.new(img)
            imgstore.put()
            user_prefs.img_id = imgstore.key.id()
        return user_prefs

    def send_driver_info(self, email):
        self.params['action'] = 'driverinfo'
        self.params['senderid'] = 'barnacle'
        self.params['receiverid'] = self.user_prefs.key.id()    
        htmlbody =  self.render_str('email/welcome.html', **self.params)
        textbody = welcome_txt 
        send_info(email, welcome_sub, textbody, htmlbody)
        
class AccountPage(ProfileHandler):
    """ User account page """
    def get(self):
        if not self.user_prefs:
            self.redirect('/#signin-box')
            return         
        if self.user_prefs: # check to see if user preferences exists
            self.params.update(self.user_prefs.params_fill())
        key = self.user_prefs.key
        self.params.update(fill_prof_stub_params(self.user_prefs.key))
        q = Message.by_receiver(key)
        self.params['newcnt'] = sum(int(m.unread) for m in q)
        self.render('user/account.html',**self.params)
        
def fill_prof_stub_params(key):
    posts = []
    for r in Route.by_userkey(key):
        posts.append(r.to_dict())
    reqs = []
    for r in Request.by_userkey(key):
        reqs.append(r.to_dict())    
    params = {
        'posts' : posts,
        'requests': reqs,
        'avg_rating': Review.avg_rating(key),
        'reviews': Review.by_receiver(key)
    }
    if params['avg_rating'] < 1:
        params['avg_rating'] = 5
    if posts:
        params['dispposts']=True
    else:
        params['dispposts']=False
    if reqs:
        params['dispreqs']=True
    else:
        params['dispreqs']=False
    d = Driver.by_userkey(key)
    if d:
        params.update(d.params_fill())
    return params
    
