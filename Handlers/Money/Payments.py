import balanced
import simplejson
import logging

from google.appengine.ext import ndb
from google.appengine.api import taskqueue

from Handlers.BaseHandler import *
from Models.User.Account import *
from Models.User.Driver import *

from Utils.data.paydefs import *

""" create bank and cc accounts """

class Payments(BaseHandler):
    def get(self, action=None):
        if action=='cc':
            self.params.update(self.user_prefs.params_fill())
            self.params['next_url'] = '/account'
            self.render('money/forms/cc.html', **self.params)
                            
    def post(self, action=None):
        if action=='bank':
            self.__banksett()
        elif action=='cc':
            self.__ccsett()
                    
    def __banksett(self): 
        self.response.headers['Content-Type'] = "application/json"
        d = Driver.by_userkey(self.user_prefs.key)
        if not d:
            response = { 'status': 'Permission Denied' }
            self.write(json.dumps(response))     
            return        
        d.bank_uri = self.request.get('bankTokenURI')
        d.bank_acctnum = self.request.get('bankAccountNum')
        d.bank_name = self.request.get('bankName')
        d.bank = True
        d.put()
        
        balanced.configure(baccount)        
        customer = create_cust(self.user_prefs)
        customer.add_bank_account(d.bank_uri)
        logging.info('Bank account recorded')
        
        response = { 'status': 'ok' }
        self.write(json.dumps(response))     
        return        
        
    def __ccsett(self): 
        uri = self.request.get('balancedCreditCardURI')        
        last4 = self.request.get('last4')   
        next = self.request.get('next_url')
        first_name = self.request.get('first_name')
        last_name = self.request.get('last_name')
        email = self.request.get('email')
        tel = self.request.get('tel')
        
        balanced.configure(baccount)        
        customer = create_cust(self.user_prefs)
        customer.add_card(uri)        
        self.user_prefs.cc = last4 
        self.user_prefs.first_name = first_name
        self.user_prefs.last_name = last_name
        if email:
            self.user_prefs.email = email
        if tel:
            self.user_prefs.tel = tel
        self.user_prefs.put()
        logging.info('Credit card recorded')
        taskqueue.add(url='/summary/selfpay/'+self.user_prefs.key.urlsafe(), method='get')
        # Update status of requests
        
        self.redirect(next)
        return             
        
def create_cust(user):
    #create customer
    # balanced.configure(testaccount)
    balanced.configure(baccount)
    if not user.cust_id:
        customer = balanced.Customer(email=user.email, facebook=user.userid).save()
        user.cust_id = customer.id
        user.put()
    else:
        customer = balanced.Customer.find('/v1/customers/' + user.cust_id)
    return customer
        