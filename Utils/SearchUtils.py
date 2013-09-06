from google.appengine.ext import ndb
from google.appengine.api import search
from Models.RouteModel import *
from Models.RequestModel import *
from Utils.Defs import miles2m
import re
import logging
ROUTE_INDEX = 'ROUTE_INDEX'
REQUEST_INDEX = 'REQUEST_INDEX'
CL_INDEX = 'CL_INDEX'


def create_route_doc(keysafe, route):
    index = search.Index(name=ROUTE_INDEX)
    u = route.userkey.get()
    startpoint = search.GeoPoint(route.start.lat,route.start.lon)
    destpoint = search.GeoPoint(route.dest.lat,route.dest.lon)
    # everything that will be returned in search results should be in a field
    doc = search.Document(doc_id=keysafe,
        fields=[search.GeoField(name='start', value=startpoint),
                search.GeoField(name='dest', value=destpoint),
                search.DateField(name='delivstart', value=route.delivstart),
                search.DateField(name='delivend', value=route.delivend),
                search.TextField(name='locstart', value=route.locstart),
                search.TextField(name='locend', value=route.locend),
                search.TextField(name='routekey', value=route.key.urlsafe()),
                search.TextField(name='userkey', value=u.key.urlsafe()),
                search.TextField(name='first_name', value=u.first_name),
                search.TextField(name='prof_url', value=u.profile_url()),
                search.TextField(name='post_url', value=route.post_url()),
                search.TextField(name='thumb_url', value=u.profile_image_url('small'))])
#get rid of extraneous stupid fields                
    try:
        index.put(doc)
    except search.Error,e:
        logging.error(e)            


def search_points(center, field, dist, index_name):
    limit = 100
    meters = dist * miles2m
    index = search.Index(index_name)
    query = 'distance('+field+', geopoint('+str(center.lat)+', '+str(center.lon)+')) < '+str(meters)
    loc_expr = 'distance('+field+', geopoint('+str(center.lat)+', '+str(center.lon)+'))'
    logging.info(query)
    # q = search.Query(query_string=query)
    # try:
        # search_results = index.search(q)
        # return search_results
    # except search.Error,e:
        # logging.error(e)
        
    sortexpr = search.SortExpression( expression=loc_expr,
      direction=search.SortExpression.ASCENDING, default_value=meters)
    search_query = search.Query( query_string=query,
       options=search.QueryOptions(limit=limit,
        sort_options=search.SortOptions(expressions=[sortexpr])))
    results = index.search(search_query)
    return results

def search_points_start_end(dist, index_name, enddate, startdate, fieldd,field0,center0, field1, center1=None):
    limit = 100
    meters = dist * miles2m
    index = search.Index(index_name)
    query = '(distance('+field0+', geopoint('+str(center0.lat)+', '+str(center0.lon)+')) < '+str(meters) + ')'
    if center1:
        query = query + ' AND (distance('+field1+', geopoint('+str(center1.lat)+', '+str(center1.lon)+')) < '+str(meters) + ')'
    else:
        query = query + ' AND (distance('+field1+', geopoint('+str(center0.lat)+', '+str(center0.lon)+')) < '+str(meters) + ')'
    query = query + ' AND (('+fieldd+' >= ' + startdate + ') OR ('+fieldd+' >= ' + enddate + '))'
    loc_expr = 'distance('+field0+', geopoint('+str(center0.lat)+', '+str(center0.lon)+'))'
    logging.info(query)
       
    sortexpr = search.SortExpression( expression=loc_expr,
      direction=search.SortExpression.ASCENDING, default_value=meters)
    search_query = search.Query( query_string=query,
       options=search.QueryOptions(limit=limit,
        sort_options=search.SortOptions(expressions=[sortexpr])))
    results = index.search(search_query)
    logging.info(results)
    return results

def search_points_end(dist, index_name, enddate, fieldd,field0,center0, field1, center1=None):
    limit = 100
    meters = dist * miles2m
    index = search.Index(index_name)
    query = '(distance('+field0+', geopoint('+str(center0.lat)+', '+str(center0.lon)+')) < '+str(meters) + ')'
    if center1:
        query = query + ' AND (distance('+field1+', geopoint('+str(center1.lat)+', '+str(center1.lon)+')) < '+str(meters) + ')'
    else:
        query = query + ' AND (distance('+field1+', geopoint('+str(center0.lat)+', '+str(center0.lon)+')) < '+str(meters) + ')'
    query = query + ' AND ('+fieldd+' <= ' + enddate + ')'
    loc_expr = 'distance('+field0+', geopoint('+str(center0.lat)+', '+str(center0.lon)+'))'
    logging.info(query)
       
    sortexpr = search.SortExpression( expression=loc_expr,
      direction=search.SortExpression.ASCENDING, default_value=meters)
    search_query = search.Query( query_string=query,
       options=search.QueryOptions(limit=limit,
        sort_options=search.SortOptions(expressions=[sortexpr])))
    results = index.search(search_query)
    logging.info(results)
    return results    
    
def debugsearch(name_index):
    index = search.Index(name_index)
    q = search.Query(query_string='')
    try:
        search_results = index.search(q)
        return search_results
    except search.Error,e:
        logging.error(e)     

def search_todict(s):
    d = {}
    for f in s.fields:
        d[f.name] = f.value
    return d
    
def create_request_doc(keysafe, route):
    index = search.Index(name=REQUEST_INDEX)
    u = route.userkey.get()
    startpoint = search.GeoPoint(route.start.lat,route.start.lon)
    destpoint = search.GeoPoint(route.dest.lat,route.dest.lon)
    # everything that will be returned in search results should be in a field
    doc = search.Document(doc_id=keysafe,
        fields=[search.GeoField(name='start', value=startpoint),
                search.GeoField(name='dest', value=destpoint),
                search.DateField(name='delivby', value=route.delivby),
                search.TextField(name='locstart', value=route.locstart),
                search.TextField(name='locend', value=route.locend),
                search.TextField(name='first_name', value=u.first_name),
                search.TextField(name='routekey', value=route.key.urlsafe()),
                search.TextField(name='userkey', value=u.key.urlsafe()),
                search.TextField(name='prof_url', value=u.profile_url()),
                search.TextField(name='post_url', value=route.post_url()),
                search.TextField(name='thumb_url', value=u.profile_image_url('small'))])
    try:
        index.put(doc)
    except search.Error,e:
        logging.error(e)            

def delete_doc(keysafe, r_name):
    if r_name == 'Route':
        index = search.Index(name=ROUTE_INDEX)
        index.delete(keysafe)
    elif r_name == 'Request':
        index = search.Index(name=REQUEST_INDEX)
        index.delete(keysafe)
    return
    