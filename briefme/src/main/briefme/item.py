from google.appengine.ext import ndb

import rdflib
import json

class Item(ndb.Model):
    '''This represents a single RSS-like item, as in a single podcast episode.
       An Item is currently identified by a name with namespace,
       e.g. a DBpedia resource like 'http://dbpedia.org/resource/Mozart'

       An Item takes a long time (say, 10-60 seconds) to create in all details,
       so this is done asynchronously. For this reason, Item has 'progress'
       and 'ready' attributes. This is somewhat redundant, as progress should be 1.0
       whenever ready is True.
    '''
    #TODO Consider closer tie between Boolean states and CSS classes in frontend
    created       = ndb.DateTimeProperty(auto_now_add = True)
    name          = ndb.StringProperty(required = True)
    namespace     = ndb.StringProperty(required = True)
    ready         = ndb.BooleanProperty(required = True,
                                        default = False)
    '''Value between 0.0 and 1.0. TODO: Verify or remodel
    '''
    progress      = ndb.FloatProperty(default = 0.01)
    failed        = ndb.BooleanProperty(required = True,
                                        default = False)
    title         = ndb.StringProperty()
    thumbnail_url = ndb.StringProperty()
    '''Currently always a list of even length on the form
       [section_0_title,section_0_text,section_1_title,section_1_text,...]
    '''
    data          = ndb.TextProperty(repeated = True)

    @staticmethod
    def for_name(name, 
                 namespace = 'http://dbpedia.org/resource/',
                 create_cb = lambda key : None):
        '''Looks up named Item.
           If there is no suchItem, a new (shallow) one is created
           and stored, and then the create_cb is called
           with its ndb.Key.
           @param name: e.g. 'Mozart'
           @param namespace: An RDF namespace, e.g. 'http://dbpedia.org/resource/'
           @param create_cb: A single-parameter callback to start
           asynchronous creation of the Item. The default is
           to do nothing.
           @return An Item instance. Never returns None.
        '''
        key = ndb.Key(Item, namespace + name)
        entity = key.get()
        if entity is None:
            entity = Item(key = key, 
                          name = name, 
                          namespace = namespace)
            entity.put()
            create_cb(key)
        return entity

    def external_url(self):
        '''@return e.g. 'http://dbpedia.org/resource/Mozart'
        '''
        return self.namespace + self.name

    def uriref(self):
        '''@return e.g. rdflib.URIRef('http://dbpedia.org/resource/Mozart')
        '''
        return rdflib.URIRef(self.external_url())

    def set_finished_with_data(self, data):
        '''Finalizes this Item.
           Sets progress to 1.0, ready to True and
           data to the given value, then stores this Item.
        '''
        self.ready = True
        self.progress = 1.0
        self.data = data
        self.put()

    def set_progress(self, progress):
        '''Utility: Updates and stores self in one operation
        '''
        self.progress = progress
        self.put()
        
    def set_title(self, title):
        '''Utility: Updates and stores self in one operation
        '''
        self.title = title
        self.put()

    def set_thumbnail_url(self, thumbnail_url):
        '''Utility: Updates and stores self in one operation
        '''
        self.thumbnail_url = thumbnail_url
        self.put()
        
    def set_failed(self, value = True):
        '''Utility: Updates and stores self in one operation
        '''
        self.failed = value
        self.put()

    def as_jsonifiable(self):
        '''Converts this Item to a structure suitable for JSON output
           Currently excludes the 'created' field (which would require 
            separate formatting).
           @return the created data structure (a dict)
        '''
        d = self.to_dict()
        del d['created']
        return d

    def write_as_json(self, writer):
        '''Dumps this Item as JSON to the writer.
           Currently excludes the 'created' field (which would require 
            separate formatting).
        '''
        json.dump(self.as_jsonifiable(), writer)


