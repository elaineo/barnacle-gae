from google.appengine.ext import ndb
from Models.Post.Offer import *

""" Delivery Offers inherit from Offer"""
       
class OfferRoute(Offer):
    """ Make an offer to deliver """
    pathpts = ndb.GeoPtProperty(repeated=True)         
           
    def print_html(cls):
        rout = cls.sender_name() + '\'s Delivery Request'
        rout += '\nDeliver By: ' + cls.deliverby.strftime('%m/%d/%Y')
        rout += '\nOffer price: ' + str(cls.price)
        return rout 
        
    def to_dict(self):
        offer = self.base_dict()
        return offer        