from google.appengine.ext import ndb
from Models.Post.Post import Post
from Models.User.Account import *
from Models.Tracker.TrackerModel import *

class RepeatRoute(ndb.Model):
    period = ndb.IntegerProperty() # weekly (0), or monthly (1)
    dayweek = ndb.IntegerProperty(repeated=True) # day of week, Sunday(0) to Sat(6) 
    weekmonth = ndb.IntegerProperty(repeated=True) # week of month1-4

class RouteStats(ndb.Model):
    views = ndb.IntegerProperty(default=0)    
    
class Route(Post):
    roundtrip = ndb.BooleanProperty(default=False)
    repeatr = ndb.StructuredProperty(RepeatRoute)
    delivstart = ndb.DateProperty(required=True)
    delivend = ndb.DateProperty(required=True)
    pathpts = ndb.GeoPtProperty(repeated=True)     
    stats = ndb.StructuredProperty(RouteStats)

    def track_url(self):
        """ if confirmed url for tracking page """
        t = TrackerModel.by_route(self.key).get()
        if t:
            return t.post_url()
        else:
            return ''        
        
    def to_dict(cls,incl_user=False):
        route = cls.base_dict()
        route.update({ 'rt' : int(cls.roundtrip),
                    'delivstart' : cls.delivstart.strftime('%m/%d/%Y'),
                    'delivend' : cls.delivend.strftime('%m/%d/%Y') })
        route.update(cls.gen_repeat())
        if incl_user:
            u = cls.key.parent().get()
            udict = {
                'prof_img' : u.profile_image_url('small'),
                'first_name' : u.nickname()
            }
            route.update(udict)        
        return route
    
    def to_search(cls):
        u = cls.key.parent().get()
        route = {
            'routekey' : cls.key.urlsafe(),
            'delivstart' : cls.delivstart.strftime('%b-%d-%y'),
            'delivend' : cls.delivend.strftime('%b-%d-%y'),
            'start' : cls.locstart,
            'dest' : cls.locend,
            'roundtrip' : int(cls.roundtrip)
        }
        if cls.details:
            route['details'] = cls.details[:200]
        if u:
            route['thumb_url'] = u.profile_image_url('small')
            route['first_name'] = u.first_name
            route['fbid'] = u.userid
        return route             
    
    def gen_repeat(self):
        r = {}
        r['repeat'] = False
        if self.repeatr:
            weekdays = ['Sunday','Monday','Tuesday','Wednesday','Thursday',
            'Friday','Saturday']
            rstring = 'Every '
            if self.repeatr.dayweek == None:
                return r
            if self.repeatr.period == 1:
                weekmonths = ['1st', '2nd', '3rd', '4th', '5th']
                mstring = ''
                for m in self.repeatr.weekmonth:
                    mstring = mstring + ' and ' + weekmonths[m]
                rstring = rstring + mstring[5:] + ' '
            for w in self.repeatr.dayweek:
                rstring = rstring + weekdays[w] + ', '
            rstring = rstring + 'until ' + self.delivend.strftime('%m/%d/%Y')
            r['repeat'] = True
            r['repeatr'] = self.repeatr.to_dict()
            r['rstring'] = rstring
        return r

    def increment_views(self):
        if self.stats:
            self.stats.views = self.stats.views+1
            self.put()
            