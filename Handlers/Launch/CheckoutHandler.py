import balanced
import simplejson

from google.appengine.ext import ndb
from google.appengine.api import mail

from Handlers.BaseHandler import *
from Handlers.Launch.ReserveHandler import fill_driver_params, fill_res_params
from Handlers.Tracker.TrackerHandler import create_from_res

from Models.Launch.Driver import *
from Models.Launch.ResModel import *
from Models.Launch.BarnacleModel import *
from Models.PaymentModel import *
from Models.UserModels import *

from Utils.data.paydefs import *
from Utils.Defs import *
from Utils.EmailUtils import send_info, create_note
from Utils.DefsEmail import *
from Utils.data.balanced import *

class CheckoutHandler(BaseHandler):
    def get(self, action=None, key=None):
        if not key:
            self.redirect('/request')
        elif not action:
            self.__checkout(key)
        elif action=='confirmhold':
            self.__confirm_hold(key)
                            
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
        
        customer = self.__create_cust(uri,email)
        charge = res.rates*100
        customer.debit(amount=charge)
        self.params['d'] = fill_driver_params(res.driver.get())
        self.params.update(fill_res_params(res))
        eparams = self.params
        eparams.update(self.params['d'])
        self.render('launch/receipt.html', **self.params)
        self.send_receipt(email, res, eparams)
        
    def __hold(self, key):
        try:
            res = ndb.Key(urlsafe=key).get()                
        except:
            self.abort(400)    
        email = self.request.get('email')
        tel = self.request.get('tel')
        msg = self.request.get('msg')
        uri = self.request.get('balancedCreditCardURI')        
        
        customer = self.__create_cust(uri,email)
        p = HoldAccount(uri = uri, userkey = self.user_prefs.key, reskey = res.key, amount = res.price)
        p.put()
        
        charge = res.price*100
        hold = balanced.Hold(source_uri=uri, amount=charge)

        # notify the driver -- add message
        res_msg = new_res_msg % key
        if msg:
            res_msg = res_msg + '\n\n----Message from Sender----\n\n' + msg
        create_note(self, res.receiver, new_res_sub, res_msg)    
        self.redirect('/reserve/' + key)  

    def __confirm_hold(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()                
        except:
            self.abort(400)    

        p = HoldAccount.by_reskey(res.key)
        
        balanced.configure(baccount)
        cust_id = p.userkey.get().cust_id
        customer = balanced.Customer.find('/v1/customers/' + cust_id)
        customer.add_card(p.uri)
            
        charge = res.price*100
        customer.debit(amount=charge)
        
        hold = balanced.Hold.find(p.uri)
        hold.void()
        p.key.delete()
        
        res.confirmed=True
        res.put()        
        d = Driver.by_userkey(res.receiver)
        self.params = d.params_fill(self.params)
        self.params['reskey'] = key
        self.params.update(res.to_dict())        
        self.send_receipt(customer.email, res, self.params) 
        # notify the driver?
        self.redirect('/reserve/'+key)
        
    def __confirm(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()                
        except:
            self.abort(400)    
        email = self.request.get('email')
        tel = self.request.get('tel')
        uri = self.request.get('balancedCreditCardURI')        

        customer = self.__create_cust(uri,email)
        charge = res.price*100
        if charge > 0:
            customer.debit(amount=charge)
        res.confirmed=True
        res.put()        
        create_from_res(res)
        d = Driver.by_userkey(res.sender)
        self.params['d'] = d.params_fill({})
        self.params['reskey'] = key
        self.params.update(res.to_dict())      
        eparams = self.params
        eparams.update(self.params['d'])
        self.render('launch/receipt.html', **self.params)
        self.send_receipt(email, res, eparams) 
        # notify the driver
        msg = self.user_prefs.first_name + confirm_do_msg % key
        create_note(self,res.sender, confirm_do_sub, msg)

    def __create_cust(self,uri,email=None):
        #create customer
        # balanced.configure(testaccount)
        balanced.configure(baccount)
        if not self.user_prefs.cust_id:
            customer = balanced.Customer(email=email, facebook=self.user_prefs.userid, card_uri = uri).save()
            u = self.user_prefs.key.get()
            u.cust_id = customer.id
            u.put()
        else:
            customer = balanced.Customer.find('/v1/customers/' + self.user_prefs.cust_id)
            customer.add_card(uri)
        return customer
        
    def __test(self):
        balanced.configure(testaccount)
        # buyer = balanced.Marketplace.my_marketplace.create_buyer(
        # 'elaine.ou2@example.com', name='Elaien Ou',
    # card_uri='/v1/marketplaces/TEST-MP59PrHkpa0ko7BaYwp0CkH5/cards/CC5voIUOldIsY8MUi14myQPR'
    # ) 
        customer = balanced.Customer().save()
        logging.info(customer.id)

    def send_receipt(self, email, res, params):
        self.params['action'] = 'receipt'
        self.params['senderid'] = 'barnacle'
        u = UserPrefs.by_email(email)
        if u:
            self.params['receiverid'] = u.key.id()
        else:
            self.params['receiverid'] = email
        htmlbody =  self.render_str('email/receipt.html', **params)
        textbody = resreceipt_txt % params
        send_info(to_email=email, subject=confirm_res_sub, 
            body=textbody, html=htmlbody)