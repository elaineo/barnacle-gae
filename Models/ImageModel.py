from google.appengine.ext import ndb
from google.appengine.api import images
from Models.UserUtils import *

class ImageStore(ndb.Model):
    """ Image datastore """
    image_orig = ndb.BlobProperty()
    image_medium = ndb.BlobProperty()
    image_small = ndb.BlobProperty()
    fakehash = ndb.StringProperty() # used to prevent scrapping
    date = ndb.DateTimeProperty(auto_now_add=True)
    def update(self, img):
        """ Automatially crop and resize """
        image_orig = img
        i = images.Image(img)
        h = float(i.height)
        w = float(i.width)

        # crop to make square image
        if h < w:
            ratio = h/w
            i.crop(0.5 - 0.5*ratio, 0.0, 0.5 + 0.5*ratio, 1.0)
        else:
            ratio = w/h
            i.crop(0.0, 0.5 - 0.5*ratio, 1.0, 0.5 + 0.5*ratio)

        # resize images
        i.resize(360, 360)
        self.image_medium = i.execute_transforms()
        i.resize(100, 100)
        self.image_small = i.execute_transforms()

        # generate fakehash        
        self.fakehash = make_salt() + make_salt()

    @classmethod
    def new(cls, img):
        """ Return instance populated by img """
        i = ImageStore()
        i.update(img)        
        return i