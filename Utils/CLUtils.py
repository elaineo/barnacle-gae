from google.appengine.ext import ndb
from google.appengine.api import search
from Models.Launch.CLModel import *
import logging
CL_INDEX = 'CL_INDEX'

def create_cl_doc(keysafe, route):
    index = search.Index(name=CL_INDEX)
    startpoint = search.GeoPoint(route.start.lat,route.start.lon)
    destpoint = search.GeoPoint(route.dest.lat,route.dest.lon)
    # everything that will be returned in search results should be in a field
    doc = search.Document(doc_id=keysafe,
        fields=[search.GeoField(name='start', value=startpoint),
                search.GeoField(name='dest', value=destpoint),
                search.DateField(name='delivend', value=route.delivby),
                search.TextField(name='locstart', value=route.locstart),
                search.TextField(name='locend', value=route.locend),
                search.TextField(name='post_url', value=route.post_url())])
                
    try:
        index.put(doc)
    except search.Error,e:
        logging.error(e)            