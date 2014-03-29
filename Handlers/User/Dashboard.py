from Handlers.BaseHandler import *
from Models.User.Account import *
from Models.User.Driver import *
import logging

        
class AccountPage(BaseHandler):
    """ User account page """
    def get(self):
        if not self.user_prefs:
            self.redirect('/')
            return         
        
        # Check to see if this is a driver or sender
        d = Driver.by_userkey(self.user_prefs.key)
        if d:
            self.params.update(d.params_fill())
            self.render('user/account/driver.html',**self.params)
        else:
            self.params.update(self.user_prefs.params_fill())        
            self.render('user/account/sender.html',**self.params)