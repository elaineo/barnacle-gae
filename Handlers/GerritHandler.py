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
from Models.RequestModel import *

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
import math
        
class GerritHandler(BaseHandler):
    def get(self, action=None):
        if action=='hello':
            gerrit = Request.query().filter(Request.rates > 0)
            
            self.write( "SUM")
            self.write(sum([g.rates for g in gerrit]) )
            
            self.write( "\n<BR>COUNT")
            self.write(gerrit.count() )

            self.write( "\n<BR>AVG")
            self.write(sum([g.rates for g in gerrit]) / gerrit.count() )

        elif action=='wow':
            self.write('Total users \t New users \t Active users \t Active reqs \t New reqs \t Reqs w matches \t Active routes \t New routes<br>')
            for weeknum in range(1,5):
                currweek = datetime.now() - timedelta(weeks=weeknum-1)
                lastweek = datetime.now() - timedelta(weeks=weeknum)
                
                # all users
                users = str(UserPrefs.query(UserPrefs.creation_date < currweek).count())
                active_week0 = str(UserPrefs.query().filter(ndb.AND(UserPrefs.last_active > lastweek, UserPrefs.last_active < currweek)).count())
                join_week0 = str(UserPrefs.query().filter(ndb.AND(UserPrefs.creation_date > lastweek, UserPrefs.creation_date < currweek)).count())
                
                # Active Barnacles
                reqs = Request.query().filter(Request.created < currweek)
                # Barnacles created in last week
                requests_week0 = str(Request.query().filter(ndb.AND(Request.created > lastweek, Request.created < currweek)).count())
                requests = str(reqs.count())            
                
                # For all active barnacles, how many have matches that were created prior to this week?
                matches = 0
                for r in reqs:
                    if r.matches:
                        try:
                            if (True in [m.get().created < currweek for m in r.matches]):
                                matches = matches + 1
                        except:
                            logging.error(r.key.urlsafe())
                
                # Active Routes
                routes = str(Route.query().filter(Route.created < currweek).count())
                routes_week0 = str(Route.query().filter(ndb.AND(Route.created > lastweek, Route.created < currweek)).count())            
                
                self.write(currweek.strftime('%Y-%m-%d') + '\t' + users + '\t' + join_week0 + '\t' + active_week0 + '\t' + requests + '\t' + requests_week0 + '\t' + str(matches) + '\t' + routes + '\t' + routes_week0 + '<br>')

        elif action=='repeat': 
            routes = Request.query()
            users = []
            rusers = []
            rcount = 0
            for r in routes:
                if r.userkey in users and r.userkey not in rusers:
                    rcount = rcount+1
                    rusers.append(r.userkey)
                else:
                    users.append(r.userkey)
            xroutes = ExpiredRequest.query()
            for r in xroutes:
                if r.userkey in users and r.userkey not in rusers:
                    rcount = rcount+1
                    rusers.append(r.userkey)
                else:
                    users.append(r.userkey)
            self.write(rcount)
        elif action=='matchdump':            
            reqdump = []
            requests = Request.query()
            for r in requests:
                dump = r.to_dict()
                if r.stats.notes:
                    dump['notes'] = r.stats.notes
                if r.stats.status:
                    dump['status'] = r.stats.status                    
                matches = []
                for q in r.matches:
                    try:
                        matches.append(q.get().to_dict())
                    except:
                        continue
                dump['matches'] = matches
                reqdump.append(dump)  
            self.params['reqdump'] = reqdump
            self.render('search/reqs_matches.html', **self.params)
        if action=='cl':

            gerrit = UserPrefs.query(UserPrefs.stats.referral.IN(['craigslist']))
            
            ### I commented this out cuz this file was preventing other stuff from running -- E
            
            # for
            # self.write( "COUNT")
            # self.write(gerrit.count() )
        
        
        #self.write( gerrit.count() )
             # delete_all_in_index(ROUTE_INDEX)
            # delete_all_in_index(REQUEST_INDEX)
        