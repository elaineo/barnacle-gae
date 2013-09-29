import urllib2
import json
import logging
import math
from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from Utils.Defs import geocode_url, directions_url

class RouteUtils():            
    def setloc(self,r,startstr,endstr):
        route=r
        # route.start,route.locstart=self.getGeoLoc(startstr)
        # route.dest,route.locend=self.getGeoLoc(endstr)
        if route.start and route.dest: 
            route.pathpts = self.getPath(route.start,route.dest)
        return route

    def setpoints(self,p,startstr,endstr):
        route=p
        route.start,route.locstart=self.getGeoLoc(startstr)
        route.dest,route.locend=self.getGeoLoc(endstr)
        if not route.start or not route.dest: 
            return None
        else:
            return route
            
    def getGeoLoc(self,location):
        loc = urllib2.quote(location)
        geo_url = geocode_url +  'address=' + loc + '&sensor=false'
        try:
            req = urlfetch.fetch(geo_url)
            results = json.loads(req.content)['results']
            logging.info(req.content)
        except:
            logging.error('HTTPError from google geo')
            raise HTTPError 
            return              
        try:
            cloc = results[0]
            lat=cloc['geometry']['location']['lat']
            lon=cloc['geometry']['location']['lng']
            geo_loc = ndb.GeoPt(lat=lat,lon=lon)
            tl = cloc['formatted_address'].split(',')
            text_loc = tl[0]+tl[1]
            return geo_loc, text_loc
        except IndexError:
            logging.error(req.content)
            logging.error('IndexError' + location)
            return None, 'invalid' 
    
    def getPath(self,start,dest):
        pathpts = [start]
        locs='origin=' + str(start) + '&destination=' + str(dest)
        #locs = locs+'&waypoints='
        dir_url = directions_url + locs + '&sensor=false'
        req = urlfetch.fetch(dir_url)
        logging.info(req.content)        
        results = json.loads(req.content)['routes'][0]['legs'][0]
        distance = results['distance']['value']
        for s in results['steps']:
            lat = s['end_location']['lat']
            lon = s['end_location']['lng']
            pathpts.append(ndb.GeoPt(lat=lat,lon=lon))
        return pathpts
        
    def dumproute(self,r):
        route = {}
        lat = sum([r.start.lat,r.dest.lat])/2
        lng = sum([r.start.lon,r.dest.lon])/2
        route['center'] = [lat,lng]
        pathpts = []
        for p in r.pathpts:
            pathpts.append([p.lat,p.lon])
        route['waypts'] = pathpts
        route['zoom'] = zoom_max(abs(r.start.lat-r.dest.lat),abs(r.start.lon-r.dest.lon))
        return json.dumps(route)

    def dumproutepts(self,r,pts):
        route = {}
        lat = sum([r.start.lat,r.dest.lat])/2
        lng = sum([r.start.lon,r.dest.lon])/2
        route['center'] = [lat,lng]
        pathpts = []
        markers = []
        for p in r.pathpts:
            pathpts.append([p.lat,p.lon])
        route['waypts'] = pathpts
        for q in pts:
            markers.append([q.lat,q.lon])
        route['zoom'] = map_zoom_pts(pts)           
        route['markers'] = markers
        return json.dumps(route)

    def dumppts(self,pts):
        route = {}
        lat = sum([x.lat for x in pts])/len(pts)
        lng = sum([x.lon for x in pts])/len(pts)
        route['center'] = [lat,lng]
        markers = []
        for q in pts:
            markers.append([q.lat,q.lon])
        route['markers'] = markers
        route['zoom'] = map_zoom_pts(pts)       
        return json.dumps(route)

    def dumptrack(self,r,pts):
        route = {}
        lat = sum([x.lat for x in pts])/len(pts)
        lng = sum([x.lon for x in pts])/len(pts)
        route['center'] = [lat,lng]
        markers = []
        for q in pts:
            markers.append([q.lat,q.lon])
        route['markers'] = markers
        route['zoom'] = map_zoom_pts(pts) 
        points = [q.loc for q in r.points]
        pathpts = []
        for p in points:
            pathpts.append([p.lat,p.lon])
        route['waypts'] = pathpts        
        return json.dumps(route)        
        
    def dumpall(self,routes):
        route = {}
        paths=[]
        lats=[]
        lngs=[]
        for r in routes:
            lats.append(r.dest.lat)
            lngs.append(r.dest.lon)
            pathpts = []
            for p in r.pathpts:
                pathpts.append([p.lat,p.lon])        
            paths.append(pathpts)
        
        if len(lats) != 0:
            lat = sum(lats)/len(lats)
            lng = sum(lngs)/len(lngs)
        else:
            lat = 0
            lng = 0
        # calculate map zoom, between 3 and 10
        maxh = max(lats) - min(lats)
        maxw = max(lngs) - min(lngs)
        route['zoom'] = zoom_max(maxh,maxw)
        route['center'] = [lat,lng]        
        route['paths'] = paths
        return json.dumps(route)
    def debugloc(self,r,startstr,endstr):
        route=r
        route.start,route.locstart=self.getGeoLoc(startstr)
        route.dest,route.locend=self.getGeoLoc(endstr)
        if not route.start or not route.dest: 
            return None
        else:
            route.pathpts = self.getPath(route.start,route.dest)
            return route
    def debugpoints(self,p,startstr,endstr):
        route=p
        route.start,route.locstart=self.getGeoLoc(startstr)
        route.dest,route.locend=self.getGeoLoc(endstr)
        if not route.start or not route.dest: 
            return None
        else:
            return route
                    
        
def map_zoom_pts(pts):
    # calculate map zoom
    lats = [x.lat for x in pts]
    lngs = [x.lon for x in pts]
    maxh = max(lats) - min(lats)
    maxw = max(lngs) - min(lngs)
    return zoom_max(maxh,maxw)-1

def zoom_max(max0,max1):
    # calculate map zoom
    b=max([1,max0+max1])
    a = math.log10(b)
    zoom = round(10-a*3.5)    
    return zoom
    
def HaversinRev(center,d):
    #return an approximate bounding box
    # d = 2r arcsin (sqrt(sin2((Lat2-Lat1)/2)+cos(Lat1)cos(Lat2)sin2((Lon2-Lon1)/2)))
    # r = 3959 miles
    c = d/7918
    h = (math.sin(c))**2
    maxLat = 2*c+center.lat
    minLat = center.lat - 2*c
    dLon = math.asin(math.sqrt(h)/(math.cos(center.lat)))
    maxLon = 2*dLon + center.lon
    minLon = center.lon - 2*dLon
    bb = { 'maxLat':maxLat, 'minLat':minLat, 'maxLon':maxLon,'minLon':minLon }
    return bb
