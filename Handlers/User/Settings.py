from Handlers.BaseHandler import *
from Models.User.Account import *
from Models.User.Driver import *
import logging

class SettingsHandler(BaseHandler):
    def get(self):
        if self.user_prefs: 
            self.params['email'] = self.user_prefs.email
            self.params['tel'] = self.user_prefs.tel
            self.params['notify'] = {'notify' : self.user_prefs.get_notify() }
            if self.user_prefs.cc:
                self.params['cc_num'] = 'XXXXXXXXXXXX'+self.user_prefs.cc
            else:
                self.params['cc_num'] = 'MISSING'
            d = Driver.by_userkey(self.user_prefs.key)
            if d:
                self.params.update(d.params_fill())
            self.render('user/forms/settings.html', **self.params)  
        else:
            self.redirect("/")
                    
    def post(self,action=None):
        self.__emailsett()        

    def __emailsett(self):        
        notify = self.request.get_all('notify')
        email = self.request.get('email')
        tel = self.request.get('tel')
        if not notify:
            settings = UserSettings(notify = [])        
        else:
            settings = UserSettings(notify = [int(n) for n in notify])        
        if self.user_prefs:
            user_prefs = self.user_prefs
            if email:
                user_prefs.email = email            
            if tel:
                user_prefs.tel = tel            
            user_prefs.settings = settings
            user_prefs.put()
        self.redirect("/account")