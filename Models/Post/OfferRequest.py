from google.appengine.ext import ndb
from Models.Post.Offer import *
from Models.ImageModel import *

class OfferRequest(Offer):
    """ Make a Reservation for existing route """
    details = ndb.TextProperty()    # description of goods
    img_id = ndb.IntegerProperty()     

    def print_html(cls):
        rout = cls.driver_name() + '\'s route from ' + cls.locstart + ' to ' + cls.locend
        rout += '\nDeliver By: ' + cls.deliverby.strftime('%m/%d/%Y')
        rout += '\nItems: ' + cls.details
        rout += '\nOffer price: ' + str(cls.price)
        return rout
        
    def image_url(self, mode = 'original'):
        """ Retrieve link to profile thumbnail or default """
        if self.img_id:
            profile_image = ImageStore.get_by_id(self.img_id)
            if profile_image:
                buf = '/img/' + str(self.img_id) + '?key=' + profile_image.fakehash
                if mode:
                    buf += '&mode=' + mode
                return buf
        return '/static/img/icons/nophoto1.png'        
        
    def to_dict(self):
        offer = self.base_dict()
        offer['details'] = self.details
        offer['img_url'] = self.image_url()
        offer['img_thumb'] = self.image_url('small')
        return offer