from Handlers.BaseHandler import BaseHandler
from google.appengine.api import mail
from Models.UserModels import UserPrefs
from Models.RouteModel import Route
from Models.RequestModel import Request
from Models.ReservationModel import Reservation
from Models.MessageModel import Message
from datetime import datetime, timedelta


class SummaryHandler(BaseHandler):
    def day_ago(self):
        return datetime.now() - timedelta(1)

    def number_of_new_users(self):
        return UserPrefs.query(UserPrefs.creation_date > self.day_ago()).count()

    def number_of_new_routes(self):
        return Route.query(Route.created > self.day_ago()).count()

    def number_of_new_requests(self):
        return Request.query(Request.created > self.day_ago()).count()

    def number_of_new_reservations(self):
        return Reservation.query(Reservation.created > self.day_ago()).count()

    def number_of_new_messages(self):
        return Message.query(Message.created > self.day_ago()).count()

    def generate_report(self):
        d = {}
        d['new_users'] = self.number_of_new_users()
        d['new_routes'] = self.number_of_new_routes()
        d['new_requests'] = self.number_of_new_requests()
        d['new_reservations'] = self.number_of_new_reservations()
        d['new_messages'] = self.number_of_new_messages()
        buf = 'In Past Day\n'
        return '\n'.join([k + ' : ' + str(d[k]) for k in d])

    def email_report(self, to_address, body):
        sender_address = 'summary@p2ppostal.appspotmail.com'
        timestamp = datetime.now().strftime('%Y/%m/%d')
        subject = 'Daily Summary for %s' % timestamp
        mail.send_mail(sender_address, to_address, subject, body)

    def get(self):
        body = self.generate_report()
        self.email_report('warren.mar@gmail.com', body)
        self.email_report('elaine.ou@gmail.com', body)
