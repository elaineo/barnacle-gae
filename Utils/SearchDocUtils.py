from google.appengine.ext import ndb
from google.appengine.api import search
from Models.Post.Route import *
from Models.Post.Request import *
from Utils.SearchUtils import search_points, search_todict
import logging
ROUTE_INDEX = 'ROUTE_INDEX'
REQUEST_INDEX = 'REQUEST_INDEX'
CITY_INDEX = 'CITY_INDEX'

def create_route_doc(keysafe, route, new_r=True):        
    index = search.Index(name=ROUTE_INDEX)
    if not new_r:
        # delete the old one first
        index.delete(keysafe)    
    u = route.key.parent().get()
    startpoint = search.GeoPoint(route.start.lat,route.start.lon)
    destpoint = search.GeoPoint(route.dest.lat,route.dest.lon)

    fields=[search.GeoField(name='start', value=startpoint),
            search.GeoField(name='dest', value=destpoint),
            search.DateField(name='delivstart', value=route.delivstart),
            search.DateField(name='delivend', value=route.delivend),
            search.TextField(name='locstart', value=route.locstart),
            search.TextField(name='locend', value=route.locend),
            search.TextField(name='fbid', value=u.userid),
            search.TextField(name='first_name', value=u.first_name),
            search.TextField(name='thumb_url', value=u.profile_image_url('small'))]
    for p in route.pathpts:
        point = search.GeoPoint(p.lat,p.lon)
        fields.append(search.GeoField(name='point', value=point))
    doc = search.Document(doc_id=keysafe, fields=fields)
    try:
        index.put(doc)
    except search.Error,e:
        logging.error(e)

def create_request_doc(keysafe, route):
    index = search.Index(name=REQUEST_INDEX)
    u = route.key.parent().get()
    startpoint = search.GeoPoint(route.start.lat,route.start.lon)
    destpoint = search.GeoPoint(route.dest.lat,route.dest.lon)
    # everything that will be returned in search results should be in a field
    doc = search.Document(doc_id=keysafe,
        fields=[search.GeoField(name='start', value=startpoint),
                search.GeoField(name='dest', value=destpoint),
                search.DateField(name='delivby', value=route.delivby),
                search.TextField(name='locstart', value=route.locstart),
                search.TextField(name='fbid', value=u.userid),
                search.TextField(name='locend', value=route.locend),
                search.TextField(name='first_name', value=u.first_name),
                search.TextField(name='thumb_url', value=u.profile_image_url('small'))])
    try:
        index.put(doc)
    except search.Error,e:
        logging.error(e)

def create_city_doc(city, point):
    index = search.Index(name=CITY_INDEX)
    locpoint = search.GeoPoint(point.lat,point.lon)

    fields=[search.GeoField(name='loc', value=locpoint),
            search.TextField(name='city', value=city)]
    doc = search.Document(fields=fields)
    try:
        index.put(doc)
    except search.Error,e:
        logging.error(e)

def delete_doc(keysafe, r_name):
    if r_name == 'Route':
        index = search.Index(name=ROUTE_INDEX)
    elif r_name == 'Request':
        index = search.Index(name=REQUEST_INDEX)
    index.delete(keysafe)
    return

def closest_city(geo_pt):
    """ Returns a dictionary of the closest_city
    d = {'city': 'Dallas', 'loc' : GeoPt()}
    """
    found_pts = search_points(geo_pt, 'loc', CITY_INDEX)
    for doc in found_pts.results:
        d = search_todict(doc)
    return d
