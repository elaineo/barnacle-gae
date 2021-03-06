from Handlers.BaseHandler import *
from Models.Mobile.Sender import *
from Utils.ValidUtils import parse_unit
import logging

class SenderMobile(BaseHandler):
    def get(self, action=None):
        if action=='get_addr':
            self.__get_addr()
        return
    
    def post(self, action=None):
        if action=='trackemail':
            self.__trackemail()
        elif action=='create_addr':
            self.__create_addr()
        else:
            return
        
    def __get_addr(self):
        # return address associated with user
        data = json.loads(self.request.body)
        logging.info(data)
        try:
            key = data.get('userkey')
            type = parse_unit(data.get('type'))
            u = ndb.Key(urlsafe=key).get()
            if not u:
                response = { 'status': 'Not a user.'}
            else:
                addrs = Address.by_userkey_type(u.key,type)
                addbook = []
                for a in addrs:
                    addbook.append(a.to_dict())
                if len(addbook) > 0:
                    response = { 'status': 'ok'}
                    response['addrs'] = addbook
                else:
                    response = { 'status': 'No addresses.'}
        except:
            response = { 'status': 'Fail.'}
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))           
    
    def __create_addr(self):
        # create address associated with a user
        data = json.loads(self.request.body)
        logging.info(data)
        try:
            key = data.get('userkey')
            u = ndb.Key(urlsafe=key).get()
            if not u:
                response = { 'status': 'Not a user.'}
            else:
                name = data.get('name')
                address = data.get('address')
                city = data.get('city')
                state = data.get('state')
                zip = data.get('zip')
                apt = data.get('apt')
                a = Address(name=name, street=address, city=city, apt=apt, state=state, zip=zip, parent=u.key)
                a.put()
                response = { 'status': 'ok', 'addrkey': a.key.urlsafe()}
        except:
            response = { 'status': 'Address Failed.'}            
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))                             
    
    def __trackemail(self):
        data = json.loads(self.request.body)
        logging.info(data)
        try:
            key = data['routekey']
            r = ndb.Key(urlsafe=key).get()
            if not r:
                response = { 'status': 'Route not found.'}
            elif not self.user_prefs:
                response = { 'status': 'Not logged in.'}
            else:
                addrs = data['emails']
                for a in addrs:
                    sender = self.user_prefs.fullname() + " via Barnacle <" + a + ">"
                    subject = (share_track_subj % {'first_name':self.user_prefs.first_name})
                    body = (share_track % {'first_name': self.user_prefs.first_name,
                        'locend' : r.locend,
                        'post_url' : r.post_url() })
                    send_info(sender, subject, body)
                response = { 'status': 'ok'}
        except:
            response = { 'status': 'Email Failed.'}            
        self.response.headers['Content-Type'] = "application/json"
        self.write(json.dumps(response))                     