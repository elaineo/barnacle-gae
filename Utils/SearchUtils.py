from google.appengine.api import search
from Utils.Defs import miles2m
import re
import logging

def search_pathpts(dist, index_name, date, datefield, center):
    limit = 100
    meters = dist * miles2m
    index = search.Index(index_name)
    query = 'distance(point, geopoint('+str(center.lat)+', '+str(center.lon)+')) < '+str(meters) + ' AND ' + datefield+ ' < ' + date
    loc_expr = 'distance(point, geopoint('+str(center.lat)+', '+str(center.lon)+'))'
    logging.info(query)
        
    sortexpr = search.SortExpression( expression=loc_expr,
      direction=search.SortExpression.ASCENDING, default_value=meters)
    dateexpr = search.SortExpression( expression='delivend', direction=search.SortExpression.ASCENDING, default_value=date)
    search_query = search.Query( query_string=query,
       options=search.QueryOptions(limit=limit,
        sort_options=search.SortOptions(expressions=[sortexpr, dateexpr])))
    results = index.search(search_query)
    logging.info(results)    
    return results        
    
def expire_pathpts(index_name, date, datefield):
    index = search.Index(index_name)
    query = datefield+ ' < ' + date        
    search_query = search.Query( query_string=query )
    results = index.search(search_query)
    logging.info(results)    
    for r in results.results:
        index.delete(r.doc_id)
    return 

def search_points(center, field, dist, index_name):
    limit = 10
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
    d['routekey'] = s.doc_id
    return d
    
def search_intersect(s0,s1):
    #return intersection based on doc_ids
    s0_ids = [s.doc_id for s in s0]
    s1_ids = [s.doc_id for s in s1]
    s_ids_int = [s for s in s0_ids if s in s1_ids]
    s_int = [s for s in s0 if s.doc_id in s_ids_int]
    return s_int
    
def field_byname(s, fname):
    for f in s.fields:
        if f.name==fname:
            return f.value
    return None
           