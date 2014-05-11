import logging
import json
import urllib
from datetime import *
from google.appengine.ext import ndb
import google.appengine.api.images
from Handlers.BaseHandler import *
from Models.Tracker.TrackerModel import *
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers


# Image Uploading
# The blobstore uploading requires the construction of a url to be submitted as
# part of a multiform form. To be compatible with the iOS app, we need to return
# the upload url which the iOS can POST to. The iOS also needs be returned the
# url of the image
# 1) ask for upload url (/imgserv/url)
# 2) post multiform to upload url (/imgserv/upload)
# 3) redirect to handler which returns a json response with image url (/imgserv/success/<resource>)
# 4) return image url in json (/imgserv/img/<resource>)
# ... then iOS posts image url with lat and long


class ImageServeHandler(BaseHandler):
    def get(self, action=None, resource=None):
        if action=='url':
            upload_url = blobstore.create_upload_url('/imgblob/upload')
            self.response.headers['Content-Type'] = "application/json"
            response = {'status':'ok'}
            response['upload_url'] = upload_url
            self.write(json.dumps(response))
        if resource and action=='success':
            self.response.headers['Content-Type'] = "application/json"
            #url = images.get_serving_url(blobstore.BlobKey(blob_key))
            url = '%s/imgserv/img/%s' % (www_home, resource)
            self.write(json.dumps({'url' : url}))
        elif resource and action=='img':
            resource = str(urllib.unquote(resource))
            blob_info = blobstore.BlobInfo.get(resource)
            self.send_blob(blob_info)

class ImageBlobHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, action=None):
        if action=='upload':
            upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
            blob_info = upload_files[0]
            self.redirect('%s/imgserv/success/%s' % (www_home, blob_info.key()))
