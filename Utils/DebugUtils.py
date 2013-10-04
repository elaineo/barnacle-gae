from datetime import *
import csv
from google.appengine.ext import ndb
from google.appengine.api import search

from Handlers.BaseHandler import *
from Models.ImageModel import ImageStore
from Models.MessageModel import Message
from Models.RequestModel import Request
from Models.ReservationModel import Reservation
from Models.ReservationModel import DeliveryOffer
from Models.RouteModel import Route
from Models.UserModels import *
from Models.Launch.BarnacleModel import *
from Models.Launch.CLModel import *
from Utils.data.fakedata import *
from Utils.SearchUtils import *
from Utils.SearchDocUtils import *
from Utils.RouteUtils import *

import json
import random

class TestUtils(BaseHandler):
    def get(self):
        self.render('test.html', **self.params)
        
class DebugUtils(BaseHandler):
    def get(self, action=None):
        if action=='clearall':
            delete_all_in_index(CL_INDEX)
            # delete_all_in_index(ROUTE_INDEX)
            # delete_all_in_index(REQUEST_INDEX)
            self.redirect('/')
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
        elif action=='clearreqs':
            data = DeliveryOffer.query()
            for d in data:
                d.key.delete()
            data = Request.query()
            for d in data:
                d.key.delete()
            delete_all_in_index(REQUEST_INDEX)                
            self.write('reqs gone.')            
        elif action=='clearroutes':
            data = Reservation.query()
            for d in data:
                d.key.delete()
            data = Route.query()
            for d in data:
                d.key.delete()
            delete_all_in_index(ROUTE_INDEX)                               
            self.write('routes gone.')
        elif action=='clearcl':
            data = CLModel.query()
            for d in data:
                d.key.delete()
            delete_all_in_index(CL_INDEX)                               
            self.write('cl stuff gone.')			
        elif action=='populate':        
            for p in fakefb:
                p = p.split()
                acct_type = p[0]
                email = p[1]
                first_name = p[3]
                last_name = p[4]
                userid = p[2]
                about = p[5]
                loc = p[6]            
                sett = UserSettings(notify=[1,2],permission=1)
                u = UserPrefs(account_type = 'fb', email = email, userid = userid, first_name = first_name, last_name = last_name, about = about, location = loc, img_id = -1, settings=sett)
                u.put()
            self.write('done.')
        elif action=='drivers':        
            for p in fakefb:
                p = p.split()
                email = p[1]
                first_name = p[3]
                last_name = p[4]
                fbid = p[2]
                about = p[5]    
                seed = random.randint(-5,10)
                u = BarnacleModel( email = email, userid=fbid, first_name = first_name, last_name = last_name, about = about, img_id=-1, seed=seed, 
                completed=0, fbnetworks = [''], fblocation = 'Mountain View, California')
                u.put()
            self.write('done.')            
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
        elif action=='repairrouteindex':
            delete_all_in_index(ROUTE_INDEX) 
            routes = Route.query().fetch()
            for r in routes:
                create_route_doc(r.key.urlsafe(), r)              
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
            logging.info(d)     
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
                cl2 = cl
                cl2.locstart = locend
                cl2.locend = locstart
                cl2.start = cl.dest
                cl2.dest = cl.start
                cl2.delivend = datetime.strptime(rtdate,'%m/%d/%Y')
                try:
                    cl2.put()
                    create_pathpt_doc(cl2.key.urlsafe(), cl2)
                except:
                    response = {'status': 'fail'}
            # try:
            cl.put()
            create_pathpt_doc(cl.key.urlsafe(), cl)
            response = { 'status': 'ok' }
            # except:
                # response = {'status': 'fail'}
                # logging.error(cl)
            self.response.headers['Content-Type'] = "application/json"
            self.write(json.dumps(response))            
        else:
            return

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