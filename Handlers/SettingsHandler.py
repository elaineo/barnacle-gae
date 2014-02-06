from Handlers.BaseHandler import *
from Models.UserModels import *
from Models.Launch.Driver import *
import logging

class SettingsHandler(BaseHandler):
    def get(self):
        if self.user_prefs: 
            self.params['email'] = self.user_prefs.email
            self.params['notify'] = {'notify' : self.user_prefs.get_notify() }
            d = Driver.by_userkey(self.user_prefs.key)
            if d:
                self.params.update(d.params_fill(self.params))
            self.render('forms/settings.html', **self.params)  
        else:
            self.redirect("/")
                    
    def post(self,action=None):
        self.__emailsett()        

    def __emailsett(self):        
        notify = self.request.get_all('notify')
        email = self.request.get('email')
        if not notify:
            settings = UserSettings(notify = [])        
        else:
            settings = UserSettings(notify = [int(n) for n in notify])        
        if self.user_prefs:
            user_prefs = self.user_prefs
            if email:
                user_prefs.email = email            
            user_prefs.settings = settings
            user_prefs.put()
        self.redirect("/")