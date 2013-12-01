import urllib2
import json
import logging
import math
import random
import time
from google.appengine.api import search
from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from Utils.Defs import geocode_url, directions_url, tz_url
from Utils.PolylineCode import poly_decode

miles2m = 1609

class RouteUtils():            
    def setloc(self,r,startstr,endstr):
        route=r
        # route.start,route.locstart=self.getGeoLoc(startstr)
        # route.dest,route.locend=self.getGeoLoc(endstr)
        if route.start and route.dest: 
            route.pathpts, d = self.getPath(route.start,route.dest)
            return route, d
        else:
            return route, None

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
            
    def getTZ(self,loc):
        ts = int(time.time())
        data = "location=" + str(loc.lat) + "," + str(loc.lon) + "&timestamp=" + ts + "&sensor=true"
        req = urlfetch.fetch(tz_url+data)
        results = json.loads(req.content)['rawOffset'] 
        return int(results)
    
    def getPath(self,start,dest):
        pathpts = [start]
        locs='origin=' + str(start) + '&destination=' + str(dest)
        # eventually add waypoints
        #locs = locs+'&waypoints='
        dir_url = directions_url + locs + '&sensor=false'
        req = urlfetch.fetch(dir_url)
        results = json.loads(req.content)['routes'][0]['legs'][0]
        precision = -1
        distance = results['distance']['value']
        for s in results['steps']:
            # distance = s['distance']['value']   #dist in metres
            polyline = s['polyline']['points']
            pathsegment = poly_decode(polyline, precision)[0::100]              
            lat = s['end_location']['lat']
            lon = s['end_location']['lng']
            pathsegment.append(ndb.GeoPt(lat=lat,lon=lon))
            pathpts = pathpts + pathsegment
        return pathpts, distance

    def estPath(self,start,dest, fudge=100):
        """ Precision of path determined by total dist.
          0.1 ~ 10 miles <-- improve later """
        locs='origin=' + str(start) + '&destination=' + str(dest)
        dir_url = directions_url + locs + '&sensor=false'
        req = urlfetch.fetch(dir_url)
        results = json.loads(req.content)['routes'][0]['legs'][0]
        dist = results['distance']['value']   #dist in metres
        logging.info(dist)
        precision = precisionDist(dist/miles2m * fudge)
        pathpts = [roundPoint(start,precision)]        
        for s in results['steps']:
            polyline = s['polyline']['points']
            pathsegment = poly_decode(polyline, precision)              
            pathpts = pathpts + pathsegment
        pathpts.append(roundPoint(dest,precision))
        return pathpts, precision
        
    def dumproute(self,r):
        route = {}
        route['center'] = findCenter([r.start, r.dest])
        pathpts = []
        for p in r.pathpts:
            pathpts.append([p.lat,p.lon])
        route['waypts'] = pathpts
        route['zoom'] = zoom_max(abs(r.start.lat-r.dest.lat),abs(r.start.lon-r.dest.lon))
        return json.dumps(route)

    def dumproutepts(self,r,pts):
        route = {}
        route['center'] = findCenter([pts[0],pts[-1]])
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
        route['center'] = findCenter(pts)
        markers = []
        for q in pts:
            markers.append([q.lat,q.lon])
        route['markers'] = markers
        route['zoom'] = map_zoom_pts(pts)       
        return json.dumps(route)

    def dumptrack(self,r,pts):
        route = {}
        route['center'] = findCenter(pts)
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
        return route
        
    def dumpreqs(self,reqs, dest=True):        
        route = {}
        markers = []
        for r in reqs:
            q = r.start
            if not dest:
                q = r.dest
            a = r.locend.split(',')
            abbrevloc = a[-3]+', '+a[-2].split()[0]
            m = {'lat': q.lat,
                'lon':q.lon,
                'loc':abbrevloc,
                'rates':r.rates,
                'url': r.post_url(),
                'delivby' : r.delivby.strftime('%m/%d/%Y') }
            markers.append(m)
        route['markers'] = markers
        return route
        
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
    
def HaversinDist(startlat, startlon, destlat, destlon):
    # d = 2r asin sqrt(haversin(lat2-lat1) + cos(lat1)cos(lat2)haversin(lon2-lon1)
    # haversin theta = sin^2(theta/2)
    
    degrees_to_radians = math.pi/180.0
        
    phi1 = (90.0 - startlat)*degrees_to_radians
    phi2 = (90.0 - destlat)*degrees_to_radians
        
    theta1 = startlon*degrees_to_radians
    theta2 = destlon*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    try:
        arc = math.acos( cos )
    except:
        logging.error(cos)
        arc = 1
    # multiply by earth's radius in miles
    return arc*3960

def precisionDist(dist):
    try:
        p = round(6-2*math.log(dist)/math.log(100))
    except:
        p=6
    return int(min(6, max(0, p)))

def roundPoint(point, prec):
    p = ndb.GeoPt(lat=round(point.lat,prec),lon=round(point.lon,prec))
    return p
    
def findCenter(pts):
    lat = sum([x.lat for x in pts])/len(pts)
    lng = sum([x.lon for x in pts])/len(pts)
    return [lat,lng]
    
def priceEst(req):
    # Estimate an offer price for a given request
    pathpts, distance = RouteUtils().getPath(req.start,req.dest)    
    if req.capacity==0:
        seats = 25
    elif req.capacity==1:
        seats = 40
    else:
        seats = 50
    gas = 0.7*distance / (35*miles2m)
    seed = random.randint(-50,50)
    price = 50 + seats + int(gas) + seed
    #TODO: take dist from fwy into account
    return price, distance, seed