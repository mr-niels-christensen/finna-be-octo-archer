from google.appengine.ext import ndb

import rdflib
import json

class Item(ndb.Model):
    created       = ndb.DateTimeProperty(auto_now_add = True)
    name          = ndb.StringProperty(required = True)
    namespace     = ndb.StringProperty(required = True)
    ready         = ndb.BooleanProperty(required = True,
                                        default = False)
    progress      = ndb.FloatProperty(default = 0.01)
    title         = ndb.StringProperty()
    thumbnail_url = ndb.StringProperty()
    data          = ndb.TextProperty(repeated = True)

    @staticmethod
    def for_name(name, 
                 namespace = 'http://dbpedia.org/resource/',
                 create_cb = lambda key : None):
        key = ndb.Key(Item, namespace + name)
        entity = key.get()
        if entity is None:
            entity = Item(key = key, 
                          name = name, 
                          namespace = namespace)
            entity.put()
            create_cb(key)
        return entity

    @staticmethod
    def for_key_urlsafe(key_urlsafe):
        key = ndb.Key(urlsafe = key_urlsafe)
        return key.get()

    def external_url(self):
        return self.namespace + self.name

    def uriref(self):
        return rdflib.URIRef(self.external_url())

    def set_data(self, data):
        self.ready = True
        self.progress = 1.0
        self.data = data
        self.put()

    #TODO Get rid of most setters
    def set_progress(self, progress):
        self.progress = progress
        self.put()
        
    def set_title(self, title):
        self.title = title
        self.put()

    def set_thumbnail(self, thumbnail_url):
        self.thumbnail_url = thumbnail_url
        self.put()
        
    def set_failed(self, exception):
        self.set_data(['Sorry, {}'.format(exception)])

    def write_as_json(self, writer):
        d = self.to_dict()
        del d['created']
        json.dump(d, writer)


