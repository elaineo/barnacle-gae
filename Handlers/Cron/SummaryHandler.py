from Handlers.BaseHandler import BaseHandler
from google.appengine.api import mail
from Models.User.Account import UserPrefs
from Models.Post.Route import Route
from Models.Post.Request import Request
from Models.Post.OfferRequest import OfferRequest
from Models.Message import Message
from datetime import datetime, timedelta
from google.appengine.ext import ndb


class SummaryHandler(BaseHandler):
    def day_ago(self):
        return datetime.now() - timedelta(1)

    def number_of_new_users(self):
        return UserPrefs.query(UserPrefs.creation_date > self.day_ago()).count()

    def new_users_report(self):
        buf = ''
        for user_pref in UserPrefs.query(UserPrefs.creation_date > self.day_ago()).iter():
            buf += ' '.join([user_pref.first_name, user_pref.last_name, user_pref.email]) + '\n'
        return buf

    def new_routes_report(self):
        buf = ''
        for route in Route.query(Route.created > self.day_ago()).iter():
            buf += ', '.join([route.locstart, route.locend]) + '\n'
        return buf

    def new_requests_report(self):
        buf = ''
        for request in Request.query(Request.created > self.day_ago()).iter():
            buf += ', '.join([request.locstart, request.locend]) + '\n'
        return buf

    def number_of_new_routes(self):
        return Route.query(Route.created > self.day_ago()).filter(Route.dead==0).count()

    def number_of_new_requests(self):
        return Request.query(Request.created > self.day_ago()).filter(Request.dead==0).count()

    def number_of_users(self):
        return UserPrefs.query().count()

    def number_of_users_last_active(self):
        return UserPrefs.query(UserPrefs.last_active > self.day_ago()).count()

    def number_of_routes(self):
        return Route.query(Route.dead==0).count()

    def number_of_requests(self):
        return Request.query(Request.dead==0).count()

    def number_of_new_reservations(self):
        return OfferRequest.query(OfferRequest.created > self.day_ago()).count()

    def number_of_new_messages(self):
        return Message.query(Message.created > self.day_ago()).count()

    def total_report(self):
        d = {}
        d['total_routes'] = self.number_of_routes()
        d['total_requests'] = self.number_of_requests()
        d['total_users'] = self.number_of_users()
        buf = 'Total\n'
        buf += '\n'.join([k + ' : ' + str(d[k]) for k in d]) + '\n'
        return buf

    def generate_report(self):
        d = {}
        d['active_users'] = self.number_of_users_last_active()
        d['new_users'] = self.number_of_new_users()
        d['new_routes'] = self.number_of_new_routes()
        d['new_requests'] = self.number_of_new_requests()
        d['new_reservations'] = self.number_of_new_reservations()
        d['new_messages'] = self.number_of_new_messages()
        buf = 'In Past Day\n'
        buf += '\n'.join([k + ' : ' + str(d[k]) for k in d]) + '\n'
        buf += '\nNew Users\n' + self.new_users_report()
        buf += '\nNew Routes\n' + self.new_routes_report()
        buf += '\nNew Requests\n' + self.new_requests_report()
        buf += self.total_report()
        return buf

    def email_report(self, to_address, subject, body):
        sender_address = 'summary@p2ppostal.appspotmail.com'
        mail.send_mail(sender_address, to_address, subject, body)

    def get(self, action=None, key=None):
        if not action:
            body = self.generate_report()
            timestamp = datetime.now().strftime('%Y/%m/%d')
            subject = 'Daily Summary for %s' % timestamp
            self.email_report('warren.mar@gmail.com', subject, body)
            self.email_report('help@gobarnacle.com', subject, body)
        elif action=='selfnote' and key:
            r = ndb.Key(urlsafe=key).get()
            if r.details:
                buf = r.details + ' from ' + r.locstart + ' to ' + r.locend
            else:
                buf = r.locstart + ' to ' + r.locend
            buf += '\n http://www.gobarnacle.com' + r.post_url()
            subject = 'New Barnacle request'
            self.email_report('help@gobarnacle.com', subject, buf)
        elif action=='selfpay' and key:
            r = ndb.Key(urlsafe=key).get()
            buf = r.fullname() + ' tried to give us a cc'
            buf += '\n http://www.gobarnacle.com' + r.profile_url()
            subject = 'New Barnacle payment account'
            self.email_report('help@gobarnacle.com', subject, buf)
