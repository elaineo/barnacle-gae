from google.appengine.ext import ndb
from google.appengine.api import search
import logging
PATHPT_INDEX = 'PATHPT_INDEX'
ZIM_INDEX = 'ZIM_INDEX'

def create_pathpt_doc(keysafe, route):
    index = search.Index(name=PATHPT_INDEX)
    startpoint = search.GeoPoint(route.start.lat,route.start.lon)
    destpoint = search.GeoPoint(route.dest.lat,route.dest.lon)    
    fields=[search.GeoField(name='start', value=startpoint),
            search.GeoField(name='dest', value=destpoint),
            search.DateField(name='delivend', value=route.delivend),
            search.TextField(name='locstart', value=route.locstart),
            search.TextField(name='locend', value=route.locend)]
    for p in route.pathpts:
        point = search.GeoPoint(p.lat,p.lon)
        fields.append(search.GeoField(name='point', value=point))
    doc = search.Document(doc_id=keysafe, fields=fields)
    try:
        index.put(doc)
    except search.Error,e:
        logging.error(e)            

def create_zim_doc(keysafe, route):
    index = search.Index(name=ZIM_INDEX)
    startpoint = search.GeoPoint(route.start.lat,route.start.lon)
    destpoint = search.GeoPoint(route.dest.lat,route.dest.lon)

    fields=[search.GeoField(name='start', value=startpoint),
            search.GeoField(name='dest', value=destpoint),
            search.DateField(name='delivend', value=route.delivend),
            search.TextField(name='locstart', value=route.locstart),
            search.TextField(name='locend', value=route.locend),
            search.TextField(name='fbid', value=route.fbid)]
    for p in route.pathpts:
        point = search.GeoPoint(p.lat,p.lon)
        fields.append(search.GeoField(name='point', value=point)) 
    doc = search.Document(doc_id=keysafe, fields=fields)                
    try:
        index.put(doc)
    except search.Error,e:
        logging.error(e)                    