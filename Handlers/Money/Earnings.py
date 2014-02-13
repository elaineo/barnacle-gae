from google.appengine.ext import ndb

from Handlers.BaseHandler import *
from Models.User.Driver import *
from Models.Money.Transaction import *
from Models.User.Account import *

class Earnings(BaseHandler):
    def get(self, action=None):
        if not self.user_prefs:
            self.redirect("/")
        if action=='summary':
            self.params['total_paid'] = "%.2f" % Transaction.earnings_by_userkey(self.user_prefs.key)
            d = Driver.by_userkey(self.user_prefs.key)
            self.params['bank_acctnum'] = d.bank_acctnum
            trans = Transaction.by_driver(self.user_prefs.key, True)
            routes = []
            for t in trans:
                routes.append(t.to_dict())
            self.params['routes'] = routes
            self.render('user/account/earnings.html', **self.params)   