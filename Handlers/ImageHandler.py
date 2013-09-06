from Handlers.BaseHandler import *
from Models.ImageModel import *

class ImagePage(BaseHandler):
    """ handles images """
    def get(self, id):
        img = ImageStore.get_by_id(int(id))
        mode = self.request.get("mode")
        fakehash = self.request.get("key")
        if img and img.fakehash == fakehash:  # pass hash test to prevent scrapping     
            self.response.headers['Content-Type'] = "image/png"
            # return original / medium / small
            if mode == '': 
                self.write(img.image_medium)
            elif mode == 'original':
                self.write(img.image_orig)
            elif mode == 'small':
                self.write(img.image_small)
            else:
                self.write(img.image_small)
        else:
            self.error(404)


