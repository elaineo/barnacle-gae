import balanced
import simplejson

from google.appengine.ext import ndb
from google.appengine.api import mail

from Handlers.BaseHandler import *
from Handlers.Launch.ReserveHandler import fill_driver_params, fill_res_params

from Models.Launch.ResModel import *
from Models.Launch.BarnacleModel import *

from Utils.Defs import confirm_res_sub
from Utils.EmailUtils import send_info
from Utils.DefsEmail import *
from Utils.data.balanced import *

class CheckoutHandler(BaseHandler):
    def get(self, key=None):
        if key:
            self.__checkout(key)
        else:
            self.redirect('/res')
                            
    def post(self, action=None, key=None):
        if not key:
            self.redirect('/request')
        elif not action:
            self.__process(key)
        elif action=='confirm':
            self.__confirm(key)
        elif action=='hold':
            self.__hold(key)
            
    def __checkout(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()                
        except:
            self.abort(400)
        self.params['d'] = fill_driver_params(res.driver.get())
        self.params.update(fill_res_params(res))
        self.params['checkout_action'] = '/checkout'
        self.render('launch/checkout.html', **self.params)        
                
    def __process(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()                
        except:
            self.abort(400)    
        email = self.request.get('email')
        details = self.request.get('details')
        uri = self.request.get('balancedCreditCardURI')        
        
        if details:
            res.details = details
            res.put()
        
        #create customer
        # test balanced.configure('a966dc28048411e3aa4e026ba7f8ec28')
        balanced.configure(baccount)
        if not self.user_prefs.cust_id:
            customer = balanced.Customer(email=email, facebook=self.user_prefs.userid, card_uri = uri).save()
            u = self.user_prefs.key.get()
            u.cust_id = customer.id
            u.put()
        else:
            customer = balanced.Customer.find('/v1/customers/' + self.user_prefs.cust_id)
            customer.add_card(uri)
        charge = res.rates*100
        customer.debit(amount=charge)
        self.params['d'] = fill_driver_params(res.driver.get())
        self.params.update(fill_res_params(res))
        eparams = self.params
        eparams.update(self.params['d'])
        self.render('launch/receipt.html', **self.params)
        self.send_receipt(email, res, eparams)
        
    def __confirm(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()                
        except:
            self.abort(400)    
        email = self.request.get('email')
        details = self.request.get('details')
        uri = self.request.get('balancedCreditCardURI')        
        
        if details:
            res.details = details
            res.put()
        
        #create customer
        # test balanced.configure('a966dc28048411e3aa4e026ba7f8ec28')
        balanced.configure(baccount)
        if not self.user_prefs.cust_id:
            customer = balanced.Customer(email=email, facebook=self.user_prefs.userid, card_uri = uri).save()
            u = self.user_prefs.key.get()
            u.cust_id = customer.id
            u.put()
        else:
            customer = balanced.Customer.find('/v1/customers/' + self.user_prefs.cust_id)
            customer.add_card(uri)
        charge = res.rates*100
        customer.debit(amount=charge)
        self.params['d'] = fill_driver_params(res.driver.get())
        self.params.update(fill_res_params(res))
        eparams = self.params
        eparams.update(self.params['d'])
        self.render('launch/receipt.html', **self.params)
        self.send_receipt(email, res, eparams)        
        
    def __test(self):
        balanced.configure('a966dc28048411e3aa4e026ba7f8ec28')
        # buyer = balanced.Marketplace.my_marketplace.create_buyer(
        # 'elaine.ou2@example.com', name='Elaien Ou',
    # card_uri='/v1/marketplaces/TEST-MP59PrHkpa0ko7BaYwp0CkH5/cards/CC5voIUOldIsY8MUi14myQPR'
    # ) 
        customer = balanced.Customer().save()
        logging.info(customer.id)
#        customer = balanced.Customer.find('/v1/customers/CU65UwQmOVUQPi3gki0bCoxh')
#        customer.debit(amount='100')

    def send_receipt(self, email, res, params):
        htmlbody =  self.render_str('email/receipt.html', **params)
        textbody = receipt_txt % params
        send_info(to_email=email, subject=confirm_res_sub, 
            body=textbody, html=htmlbody)