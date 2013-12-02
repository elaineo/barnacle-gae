from datetime import *
import dateutil.parser
from google.appengine.ext import ndb
from google.appengine.api import search
from google.appengine.api import taskqueue

from Handlers.BaseHandler import *
from Models.ImageModel import ImageStore
from Models.MessageModel import Message
from Models.RequestModel import Request
from Models.ReservationModel import Reservation
from Models.ReservationModel import DeliveryOffer
from Models.RouteModel import Route
from Models.UserModels import *
from Models.Launch.Driver import *
from Models.Launch.DriverModel import *
from Models.Launch.BarnacleModel import *
from Models.Launch.CLModel import *
from Utils.data.fakedata import *
from Utils.data.citylist import *
from Utils.data.fix_cityshit import *
from Utils.SearchUtils import *
from Utils.SearchDocUtils import *
from Utils.SearchScraped import *
from Utils.RouteUtils import *

import json
import random
import logging

class TestUtils(BaseHandler):
    def get(self):
        self.render('test.html', **self.params)
        
class DebugUtils(BaseHandler):
    def get(self, action=None):
        if action=='clearall':
            delete_all_in_index(ZIM_INDEX)
            ndb.delete_multi( ZimModel.query().fetch(keys_only=True))
            # delete_all_in_index(ROUTE_INDEX)
            # delete_all_in_index(REQUEST_INDEX)
        elif action=='qtask':
            taskqueue.add(url='/debug/clearall')
        elif action=='cities':
            delete_all_in_index(CITY_INDEX)
            for c in cities:
                point = ndb.GeoPt(c['lat'],c['lon'])
                create_city_doc(c['city'],point)
            self.write('cities created')
        elif action=='clearusers':
            data = ImageStore.query()
            for d in data:
                d.key.delete()
            data = Review.query()
            for d in data:
                d.key.delete()
            data = UserAccounts.query()
            for d in data:
                d.key.delete()
            data = UserPrefs.query()
            for d in data:
                d.key.delete()                
            self.write('users gone.')
        elif action=='importusers':
            users = Request.query()
            ujson = []
            ids = []
            for u in users:
                try:                    
                    ids.append(int(u.userkey.get().userid))
                except:
                    continue
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(ids))
        elif action=='updatenotify':
            data = UserPrefs.query(UserPrefs.creation_date < datetime.now()-timedelta(days=5))
            for d in data:
                d.settings.notify.append(4)
                d.put()
            return
        elif action=='clearcl':
            data = CLModel.query()
            for d in data:
                d.key.delete()
            delete_all_in_index(CL_INDEX)                               
            self.write('cl stuff gone.')                     
        elif action=='createroutes':  
            users = BarnacleModel.query().fetch()
            for r in fakeroutes2:
                r = r.split()                
                ukey = random.choice(users).key
                p = Route(userkey=ukey, locstart=r[0], locend=r[1], capacity=0, 
                delivstart=datetime.strptime(r[2],'%m/%d/%Y'), 
                delivend=datetime.strptime(r[3],'%m/%d/%Y'))
                try:
                    p = RouteUtils().debugloc(p, p.locstart, p.locend)                  
                    p.put() 
                    create_route_doc(p.key.urlsafe(), p)                    
                except:
                    continue
            self.write('routes created.')         
        elif action=='createreqs':  
            users = UserPrefs.query().fetch()
            for r in fakereqs:
                r = r.split()                
                ukey = random.choice(users).key
                p = Request(userkey=ukey, rates=random.randrange(100), 
                locstart=r[0], locend=r[1], delivby=datetime.strptime(r[2],'%m/%d/%Y'),
                items=r[3].replace('-',' '))
                p = RouteUtils().debugpoints(p, p.locstart, p.locend)    
                p.put()            
                create_request_doc(p.key.urlsafe(), p)
            self.write('requests created.')            
        elif action=='createreviews':  
            users = UserPrefs.query().fetch()
            for r in fakereviews:  
                ukey0 = random.choice(users).key
                ukey1 = random.choice(users).key
                p = Review(sender=ukey0, receiver=ukey1, rating=5, content=r)
                p.put()            
            for r in fakerevE:
                ukey = random.choice(users).key
                receiver = UserPrefs.by_email('elaine.ou@gmail.com')
            self.write('requests created.')     
        elif action=='createcl':   
            # need to make a dummy call because strptime has problems with multithreading
            datetime.strptime('2012-01-01', '%Y-%m-%d')
            self.render('share/cldata.html', **self.params)
    
    def post(self, action=None):        
        if action=='createcl':
            d = json.loads(self.request.body)
            email = d['email']
            time = d['time']
            subj = d['subj']
            url = d['url']
            details = d['details']
            locstart = d['start']
            locend = d['dest']
            date = d['date']
            startlat = d['startlat']
            startlng = d['startlng']
            destlat = d['destlat']
            destlng = d['destlng']
            try:
                rtdate = d['rtdate']
            except:
                rtdate = None
            cl = CLModel(email = email, 
                posted = datetime.fromtimestamp(int(time) // 1000),
                clurl = url, delivend = datetime.strptime(date,'%m/%d/%Y'),
                locstart = locstart, locend = locend, 
                start = ndb.GeoPt(lat=startlat, lon=startlng),
                dest = ndb.GeoPt(lat=destlat, lon=destlng),
                details = details)
            if rtdate:
                cl2 = CLModel(email = email, 
                posted = datetime.fromtimestamp(int(time) // 1000),
                clurl = url, delivend = datetime.strptime(rtdate,'%m/%d/%Y'),
                locstart = locend, locend = locstart, 
                dest = ndb.GeoPt(lat=startlat, lon=startlng),
                start = ndb.GeoPt(lat=destlat, lon=destlng),
                details = details)
                #try:
                cl2.put()
                create_pathpt_doc(cl2.key.urlsafe(), cl2)
                # except:
                    # response = {'status': 'fail'}
            #try:
            cl.put()
            create_pathpt_doc(cl.key.urlsafe(), cl)
            response = { 'status': 'ok' }
            # except:
                # response = {'status': 'fail'}
                # logging.error(cl)
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(response))            
        elif action=='createz':
            d = json.loads(self.request.body)
            url = d['url']
            fbid = d['fbid']
            details = d['details']
            locstart = d['start']
            locend = d['dest']
            try:
                date = fix_zdate(d['date'])
            except:
                return
            startlat = d['startlat']
            startlng = d['startlng']
            destlat = d['destlat']
            destlng = d['destlng']
            
            try:
                rtdate = fix_zdate(d['rtdate'])
                details = d['date'] + ', ' + d['rtdate'] + '\n' + details
            except:
                rtdate = None
                details = d['date'] + '\n' + details
            z = ZimModel(fbid = fbid, 
                clurl = url, delivend = date,
                locstart = locstart, locend = locend, 
                start = ndb.GeoPt(lat=startlat, lon=startlng),
                dest = ndb.GeoPt(lat=destlat, lon=destlng),
                details = details)
            z.put()
            if z.distance > 160900:
                create_zim_doc(z.key.urlsafe(), z) 
            else:
                z.key.delete()
                rtdate = None
            if rtdate:
                z2 = ZimModel(fbid = fbid, 
                clurl = url, delivend = rtdate,
                locstart = locend, locend = locstart, 
                dest = ndb.GeoPt(lat=startlat, lon=startlng),
                start = ndb.GeoPt(lat=destlat, lon=destlng),
                details = details)
                # try:
                z2.put()
                create_zim_doc(z2.key.urlsafe(), z2)
                # except:
                    # response = {'status': 'fail'}
            # try:
            response = { 'status': 'ok' }
            # except:
                # response = {'status': 'fail'}
                # logging.error(z)
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(response))          
        else:
            return
            
            
def fix_zdate(date):
    d = date.split(',')
    return dateutil.parser.parse(d[-1])
    
def delete_all_in_index(index_name):
    """Delete all the docs in the given index."""
    doc_index = search.Index(name=index_name)

    while True:
        # Get a list of documents populating only the doc_id field and extract the ids.
        document_ids = [document.doc_id
                        for document in doc_index.get_range(ids_only=True)]
        if not document_ids:
            break
        # Delete the documents for the given ids from the Index.
        doc_index.delete(document_ids)