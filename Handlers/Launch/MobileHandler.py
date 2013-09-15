from Handlers.BaseHandler import *
from Utils.EmailUtils import send_info
from Utils.MobileDefs import *

class MobileHandler(BaseHandler):
    def get(self, action=None, key=None):
        self.__trackemail()
        return
    
    def post(self, action=None):
        if action=='trackemail':
            self.__trackemail()
        else:
            return
            
            
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