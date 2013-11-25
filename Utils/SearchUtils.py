from google.appengine.api import search
from Utils.Defs import miles2m
import re
import logging

def search_pathpts(dist, index_name, date, datefield, center):
    """
    Args:
        dist: radius to search in miles
        index_name:
        date:
        datefield:
        center: GeoPt where search is centered around
    Returns:

    """
    limit = 500
    meters = dist * miles2m
    index = search.Index(index_name)
    query = 'distance(point, geopoint('+str(center.lat)+', '+str(center.lon)+')) < '+str(meters) + ' AND ' + datefield+ ' < ' + date
    loc_expr = 'distance(point, geopoint('+str(center.lat)+', '+str(center.lon)+'))'

    sortexpr = search.SortExpression( expression=loc_expr,
      direction=search.SortExpression.ASCENDING, default_value=meters)
    dateexpr = search.SortExpression( expression='delivend', direction=search.SortExpression.ASCENDING, default_value=date)
    search_query = search.Query( query_string=query,
       options=search.QueryOptions(limit=limit,
        sort_options=search.SortOptions(expressions=[sortexpr, dateexpr])))
    results = index.search(search_query)
    # logging.debug(results)
    return results

def search_points_start(dist, index_name, enddate, startdate, fieldd,field,center):
    limit = 10
    meters = dist * miles2m
    index = search.Index(index_name)
    #query = '(distance('+field+', geopoint('+str(center.lat)+', '+str(center.lon)+')) < '+str(meters) + ')'
    query = '(('+fieldd+' >= ' + startdate + ') AND ('+fieldd+' <= ' + enddate + '))'
    loc_expr = 'distance('+field+', geopoint('+str(center.lat)+', '+str(center.lon)+'))'
    logging.info(loc_expr)

    sortexpr = search.SortExpression( expression=loc_expr,
      direction=search.SortExpression.ASCENDING, default_value=meters)
    search_query = search.Query( query_string=query,
       options=search.QueryOptions(limit=limit,
        sort_options=search.SortOptions(expressions=[sortexpr])))
    results = index.search(search_query)
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

def search_points(center, field, index_name):
    # find nearest matching point
    limit = 1
    meters = 500 * miles2m
    index = search.Index(index_name)
    query = ''
    loc_expr = 'distance('+field+', geopoint('+str(center.lat)+', '+str(center.lon)+'))'

    sortexpr = search.SortExpression( expression=loc_expr,
      direction=search.SortExpression.ASCENDING, default_value=meters)
    search_query = search.Query( query_string=query,
       options=search.QueryOptions(limit=limit,
        sort_options=search.SortOptions(expressions=[sortexpr])))
    results = index.search(search_query)
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
    rk = s.doc_id
    if rk.endswith('_RT'):
        d['routekey'] = rk[:-3]
    else:
        d['routekey'] = rk
    return d

def search_intersect(s0,s1):
    #return intersection based on doc_ids
    s0_ids = [s.doc_id for s in s0]
    s1_ids = [s.doc_id for s in s1]
    s_ids_int = [s for s in s0_ids if s in s1_ids]
    s_int = [s for s in s0 if s.doc_id in s_ids_int]
    return s_int[:10]

def field_byname(s, fname):
    for f in s.fields:
        if f.name==fname:
            return f.value
    return None