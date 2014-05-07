from google.appengine.ext import ndb


class Sitemap(ndb.Model):
    """
    Datastore object to contain the sitemap, because it takes too long to compute
    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    sitemap = ndb.TextProperty()

    @classmethod
    def retrieve_contents(cls):
        q = cls.query().get()
        if q:
            return q.sitemap
        else:
            return '' # default sitemap

    @classmethod
    def update_contents(cls, sitemap):
        q = cls.query().get()
        if q:
            q.sitemap = sitemap
            q.put()
        else:
            q = cls(sitemap = sitemap)
            q.put()
