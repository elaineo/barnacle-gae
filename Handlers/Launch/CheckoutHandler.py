import balanced
import simplejson

from google.appengine.ext import ndb
from google.appengine.api import mail

from Handlers.BaseHandler import *
from Handlers.Mobile.Tracker import create_from_res

from Models.User.Driver import *
from Models.Money.PaymentModel import *
from Models.User.Account import *
from Models.Post.Reservation import *

from Utils.ValidUtils import parse_rate
from Utils.data.paydefs import *
from Utils.EmailUtils import send_info, create_note
from Utils.data.EmailAddr import www_home
from Utils.Email.Reservation import *
from Utils.Email.Transact import *

class CheckoutHandler(BaseHandler):
    def get(self, action=None, key=None):
        if not key:
            self.redirect('/request')
        elif not action:
            self.__checkout(key)
        elif action=='confirmhold':
            self.__confirm_hold(key)
        elif action=='payout':
            self.__release(key)

    def post(self, action=None, key=None):
        if action=='bank':
            self.__banksett()
        elif not action:
            self.__process(key)
        elif action=='confirm':
            self.__confirm(key)
        elif action=='hold':
            self.__hold(key)
        elif action=='res':
            self.__process_anon(key)

    def __checkout(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()
        except:
            self.abort(400)
        self.params.update(res.to_dict())
        self.params['reskey'] = key
        self.params['sugg_rates'] = res.stats.sugg_price
        self.params['checkout_action'] = '/checkout/' + key
        self.render('launch/fillcheckout.html', **self.params)

    def __process(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()
        except:
            self.abort(400)
        email = self.request.get('email')
        tel = self.request.get('tel')
        rates = self.request.get('rates')
        rates = parse_rate(rates)
        uri = self.request.get('balancedCreditCardURI')

        res.rates = rates
        res.put()

        customer = self.__create_cust(email)
        customer.add_card(uri)
        charge = res.rates*100
        if charge > 0:
            customer.debit(amount=charge)
        self.params.update(res.to_dict())
        driver = res.driver.get()
        self.params['email'] = driver.email
        self.params['disp_driver'] = True
        eparams = self.params
        ## THIS ASSUMES DRIVER HAS BEEN RESERVED
        self.render('money/receipt/reservation.html', **self.params)
        self.send_receipt(email, res, eparams)

    def __process_anon(self,key):
        #Make an anonymous booking
        try:
            res = ndb.Key(urlsafe=key).get()
        except:
            logging.error('could not find res')
            self.abort(400)
        email = self.request.get('email')
        tel = self.request.get('tel')
        name = self.request.get('name')
        uri = self.request.get('balancedCreditCardURI')
        fee = self.request.get('fee')

        customer = self.__create_anon(email,tel,name)
        logging.info(customer)
        logging.info(uri)
        try:
            q = customer.add_card(uri)
        except:
            logging.error('Card error. Check Balanced')
        charge = res.rates*100
        if fee:
            charge = charge + parse_rate(fee)
        if charge > 0:
            try:
                customer.debit(amount=charge)
            except:
                logging.error('Charge error. Check Balanced')
        self.params.update(res.to_dict())
        self.params['disp_driver'] = False
        eparams = self.params
        self.render('money/receipt/reservation.html', **self.params)
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

        customer = self.__create_cust(email)
        customer.add_card(uri)
        p = HoldAccount(uri = uri, userkey = self.user_prefs.key, reskey = res.key, amount = res.rates)
        p.put()

        charge = res.rates*100
        hold = balanced.Hold(source_uri=uri, amount=charge)

        # notify the driver -- add message
        res_msg = new_res_msg % key
        if msg:
            res_msg = res_msg + '\n\n----Message from Sender----\n\n' + msg
        create_note(self, res.driver, new_res_sub, res_msg)
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

        charge = res.rates*100
        if charge >0:
            customer.debit(amount=charge)

        hold = balanced.Hold.find(p.uri)
        hold.void()
        p.key.delete()

        res.confirmed=True
        res.put()
        d = Driver.by_userkey(res.driver)
        self.params = d.params_fill()
        self.params['reskey'] = key
        self.params.update(res.to_dict())

        self.params['disp_driver'] = True
        self.send_receipt(customer.email, res, self.params)
        # notify the driver?
        self.redirect('/reserve/'+key)

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
        customer = self.__create_cust(self.user_prefs.email)
        customer.add_bank_account(d.bank_uri)

        response = { 'status': 'ok' }
        self.write(json.dumps(response))
        return

    def __release(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()
        except:
            self.abort(400)
        t = Transaction.by_reservation(key)

        logging.info(t)
        if t and not t.paid:
            driver = Driver.by_userkey(t.driver)
            balanced.configure(baccount)

            email = Transaction.driver.get().email
            customer = self.__create_cust(email)
            customer.credit(amount=res.rates)

            t.paid = True
            t.payout = res.rates
            t.put()
            #notify


    def __confirm(self,key):
        try:
            res = ndb.Key(urlsafe=key).get()
        except:
            self.abort(400)
        email = self.request.get('email')
        tel = self.request.get('tel')
        uri = self.request.get('balancedCreditCardURI')

        customer = self.__create_cust(email)
        customer.add_card(uri)
        charge = res.rates*100
        if charge > 0:
            customer.debit(amount=charge)
        res.confirmed=True
        res.put()
        create_from_res(res)
        d = Driver.by_userkey(res.driver)
        self.params['d'] = d.params_fill()
        self.params['reskey'] = key
        self.params.update(res.to_dict())
        driver = res.driver.get()
        self.params['email'] = driver.email
        self.params['disp_driver'] = True
        eparams = self.params
        eparams.update(self.params['d'])
        self.render('money/receipt/reservation.html', **self.params)
        self.send_receipt(email, res, eparams)
        # notify the driver
        msg = self.user_prefs.first_name + confirm_do_msg % key
        create_note(self,res.driver, confirm_do_sub, msg)

    def __create_cust(self,email=None):
        #create customer
        # balanced.configure(testaccount)
        balanced.configure(baccount)
        if not self.user_prefs.cust_id:
            customer = balanced.Customer(email=email, facebook=self.user_prefs.userid).save()
            u = self.user_prefs.key.get()
            u.cust_id = customer.id
            u.put()
        else:
            customer = balanced.Customer.find('/v1/customers/' + self.user_prefs.cust_id)
        return customer

    def __create_anon(self,email=None,tel=None, name=None):
        #create anonymous customer
        balanced.configure(baccount)
        customer = balanced.Customer(email=email, phone=tel, name=name).save()
        return customer

    def __test(self):
        balanced.configure(testaccount)
        # buyer = balanced.Marketplace.my_marketplace.create_buyer(
        # 'elaine.ou2@example.com', name='Elaien Ou',
    # card_uri='/v1/marketplaces/TEST-MP59PrHkpa0ko7BaYwp0CkH5/cards/CC5voIUOldIsY8MUi14myQPR'
    # )
        customer = balanced.Customer().save()
        logging.info(customer.id)

    def send_receipt(self, email, res, params, anon=False):
        htmlbody =  self.render_str('email/receipt.html', **params)
        if anon:
            textbody = resreceipt_txt % params
        else:
            textbody = resreceipt_anon % params
        send_info(to_email=email, subject=confirm_res_sub,
            body=textbody, html=htmlbody)

