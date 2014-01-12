from datetime import *
from google.appengine.ext import ndb
from google.appengine.api import search

from Handlers.BaseHandler import *
from Models.RouteModel import *
from Models.RequestModel import *
from Models.ReservationModel import *
from Models.Launch.CLModel import *
from Utils.SearchDocUtils import *
from Utils.SearchScraped import *
from Utils.SearchUtils import expire_pathpts

import json
import logging

class ExpireHandler(BaseHandler):
    def get(self):
        deaddump={}
        now = date.today()
        expire_pathpts(PATHPT_INDEX, now.strftime('%Y-%m-%d'), "delivend")
        
        deadroutes = Route.query().filter(Route.delivend<now)
        drouts=[]
        dresv=[] 
        route_index = search.Index(name=ROUTE_INDEX)
        for r in deadroutes:
            exr = ExpiredRoute(userkey=r.userkey, capacity=r.capacity, 
            details=r.details, delivstart = r.delivstart, delivend=r.delivend,
            locstart=r.locstart, locend=r.locend, 
            start=r.start, dest=r.dest, repeatr=r.repeatr, oldkey=r.key)
            exr.put()
            route_index.delete(r.key.urlsafe())
            if r.roundtrip:
                route_index.delete(r.key.urlsafe()+'_RT')
            drouts.append(exr.to_dict())
            for q in Reservation.by_route(r.key):
                if q.confirmed:
                    exp = ExpiredReservation(sender=q.sender, receiver=q.receiver, 
                    route=q.route, items=q.items, price=q.price,
                    deliverby=q.deliverby, start=q.start, dest=q.dest, 
                    locstart=q.locstart, locend=q.locend, 
                    sender_name=q.sender_name(), rcvr_name=q.receiver_name(),
                    img_id=q.img_id)
                    exp.put()
                    dresv.append(exp.to_dict())
                q.key.delete()
            r.key.delete()
        deadreqs = Request.query().filter(Request.delivby<now)
        dreqs=[]
        doff=[]
        req_index = search.Index(name=REQUEST_INDEX)
        for r in deadreqs:
            exr = ExpiredRequest(userkey=r.userkey, rates=r.rates, oldkey=r.key, 
            locstart=r.locstart, locend=r.locend, img_id=r.img_id, stats=r.stats,
            items=r.items, delivby = r.delivby, start=r.start, dest=r.dest)
            exr.put()
            req_index.delete(r.key.urlsafe())
            r.key.delete()
            drouts.append(exr.to_dict())
            for q in DeliveryOffer.by_route(r.key):
                if q.confirmed:
                    exp = ExpiredOffer(sender=q.sender, receiver=q.receiver, 
                    route=q.route, price=q.price, 
                    deliverby=q.deliverby, locstart=q.locstart, locend=q.locend, 
                    sender_name=q.sender_name(),rcvr_name=q.receiver_name())
                    exp.put()
                    doff.append(exp.to_dict())
                q.key.delete()
        # Orphan reservations
        deadres = Reservation.query().filter(Reservation.deliverby<now) 
        for q in deadres:
            if q.confirmed:
                exp = ExpiredReservation(sender=q.sender, receiver=q.receiver, 
                route=q.route, items=q.items, price=q.price,
                deliverby=q.deliverby, start=q.start, dest=q.dest, 
                locstart=q.locstart, locend=q.locend, 
                sender_name=q.sender_name(), rcvr_name=q.receiver_name(),
                img_id=q.img_id)
                exp.put()
                dresv.append(exp.to_dict())
            q.key.delete()            
        deadreq = DeliveryOffer.query().filter(DeliveryOffer.deliverby<now) 
        for q in deadreq:
            if q.confirmed:
                exp = ExpiredReservation(sender=q.sender, receiver=q.receiver, 
                route=q.route, items=q.items, price=q.price,
                deliverby=q.deliverby, start=q.start, dest=q.dest, 
                locstart=q.locstart, locend=q.locend, 
                sender_name=q.sender_name(), rcvr_name=q.receiver_name(),
                img_id=q.img_id)
                exp.put()
                doff.append(exp.to_dict())
            q.key.delete()            

            
        deadcl = CLModel.query().filter(CLModel.delivend<now)
        cl_index = search.Index(name=PATHPT_INDEX)
        bodycount = 0
        for r in deadcl:
            cl_index.delete(r.key.urlsafe())
            r.key.delete()
            bodycount=bodycount+1            
        logging.info(str(bodycount) + ' CL entries deleted')
        
        deadz = ZimModel.query().filter(ZimModel.delivend<now)
        z_index = search.Index(name=ZIM_INDEX)
        for r in deadz:
            z_index.delete(r.key.urlsafe())
            r.key.delete()
        
        hourago = datetime.now() - timedelta(minutes=60)
        deadsearch = SearchEntry.query().filter(SearchEntry.created < hourago)
        for s in deadsearch:
            s.key.delete()            
                
        deaddump['exp_routes'] = drouts
        deaddump['exp_requests'] = dreqs
        deaddump['exp_reservations'] = dresv
        deaddump['exp_offers'] = doff
        self.response.headers['Content-Type'] = "application/json"
        self.response.out.write(deaddump)