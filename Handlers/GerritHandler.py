from google.appengine.ext import ndb

from Handlers.BaseHandler import *
from Models.Message import *
from Models.Post.Request import *
from Models.Post.Route import *
from Models.Post.Post import *
from Utils.RouteUtils import *
from Utils.SearchUtils import search_pathpts, search_todict, search_intersect, field_byname
from Utils.data.citylist import cities


import json
import logging
import urllib

city_dict = {}
for c in cities:
    city_dict[c['city']] = ndb.GeoPt(c['lat'], c['lon'])
        
class GerritHandler(BaseHandler):
    def get(self, action=None, loc=None):
        if loc and action=='start':
            origin = urllib.unquote(loc)
            posts, center = self.__get_routes_from(origin)
            drivers = list(set(dump_results(posts)))
            self.write(json.dumps(drivers))
    
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
                if r.key.parent() in users and r.key.parent() not in rusers:
                    rcount = rcount+1
                    rusers.append(r.key.parent())
                else:
                    users.append(r.key.parent())
            xroutes = ExpiredRequest.query()
            for r in xroutes:
                if r.key.parent() in users and r.key.parent() not in rusers:
                    rcount = rcount+1
                    rusers.append(r.key.parent())
                else:
                    users.append(r.key.parent())
            self.write(rcount)
        elif action=='matchdump':            
            reqdump = []
            requests = Request.query()
            for r in requests:
                dump = r.to_dict()
                dump['key'] = r.key.urlsafe()
                if r.stats:
                    if r.stats.status > 10:
                        continue
                    dump['notes'] = r.stats.notes
                    dump['status'] = RequestStatus[r.stats.status]
                matches = []
                for q in r.matches:
                    try:
                        qq = q.get()
                        if qq.dead==0:
                            matches.append(qq.to_dict())
                    except:
                        continue
                dump['matches'] = matches
                reqdump.append(dump)  
            self.params['reqdump'] = reqdump
            self.render('search/reqs_matches.html', **self.params)

    
    def post(self, action=None):
        if action=='status':
            self.response.headers['Content-Type'] = "application/json"
            data = json.loads(unicode(self.request.body, errors='replace'))
            logging.info(data)
            key = data.get('key')
            if key:
                r=ndb.Key(urlsafe=key).get()
            status = data.get('status')
            if r.stats:
                r.stats.status = int(status)
            else:
                r.stats = ReqStats(status = int(status))
            r.put()
            
    def __get_routes_from(self, origin):
        if origin not in city_dict:
            return []
        start = city_dict[origin]
        delivend = datetime.now() + timedelta(days=365)
        dist = 100  # miles
        results = search_pathpts(
            dist, 'ROUTE_INDEX', delivend.strftime('%Y-%m-%d'), 'delivstart', start).results
        keepers = []
        for c in results:
            startpt = field_byname(c, "start")
            dist0 = HaversinDist(
                start.lat, start.lon, startpt.latitude, startpt.longitude)
            if dist0 < dist:
                keepers.append(c)
        return keepers, [start.lat,start.lon]            
        
        
def dump_results(results):
    posts = []
    drivers = []
    for doc in results:
        d = search_todict(doc)
        posts.append(d)        
    results = [ndb.Key(urlsafe=p['routekey']).get() for p in posts]           
    for r in results:
        try:
            u = r.key.parent()
            drivers.append(u.get().email)
        except:
            continue
    return drivers