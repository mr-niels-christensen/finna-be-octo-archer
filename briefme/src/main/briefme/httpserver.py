from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import logging
import webapp2
import json

from briefme import analyse
from briefme.webgraph import UnavailableError
from briefme.channel import Channel
from briefme.item import Item

def _task(key):
    '''Initiates the creation of an Item by putting its
       key on a taskqueue to be handled by _CreateItemHandler later
       @param key: An ndb.Key to an existing (stored) Item
    '''
    taskqueue.add(url        = '/create-item',
                  queue_name = 'addeverything', 
                  params     = {'key_urlsafe': key.urlsafe()}
    )

class _GetItemDbpediaResourceHandler(webapp2.RequestHandler):
    def get(self, name):
        '''Looks up the named Item and responds with a JSON rendering of that Item.
           If the Item did not exist, its creation is ordered on a
           taskqueue.
           @param name: The name of an Item in namespace 'http://dbpedia.org/resource/'
        '''
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        item = Item.for_name(name, create_cb = _task)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        item.write_as_json(self.response)

class _CreateItemHandler(webapp2.RequestHandler):
    def post(self):
        '''Creates an Item, updating its progress continously.
           This is a long-running process (i.e. 10-60 seconds).
           The request must map 'key_urlsafe' to the urlsafe key
           of an existing Item.
           If successful, the response will be "OK" in plain text.
        '''
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        item = ndb.Key(urlsafe = self.request.get('key_urlsafe')).get()
        try:
            item.set_failed(False)
            analyse.brief(item)
        except UnavailableError as ue:
            logging.warn('Failed to process {}'.format(item), exc_info = True);
            item.set_failed()
            raise ue # Retry according to queue settings
        except Exception as e:
            logging.warn('Failed to process {}'.format(item), exc_info = True);
            item.set_failed(e) # Do not retry
        self.response.write("OK")

class _GetChannelHandler(webapp2.RequestHandler):
    def get(self):
        '''Looks up (or creates) the current user's Channel
           and responds with a JSON rendering of that.
        '''
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        channel = Channel.for_user(users.get_current_user())
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        channel.write_as_json(self.response)

class _AddToChannelHandler(webapp2.RequestHandler):
    def post(self, name):
        '''Looks up (or creates) the current user's Channel,
           then adds the named Item to that Channel.
           If the Item did not exist, it will be created.
           Responds with a JSON rendering of the named Item.
           @param name: The name of an Item in namespace 'http://dbpedia.org/resource/'
        '''
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        channel = Channel.for_user(users.get_current_user())
        item = Item.for_name(name, create_cb = _task)
        channel.add_item(item.key)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        item.write_as_json(self.response)

#TODO better naming of URLs
application = webapp2.WSGIApplication([
    webapp2.Route(r'/get-item/dbpedia-resource/<name>', handler=_GetItemDbpediaResourceHandler, name='get-item'),
    webapp2.Route(r'/create-item', handler=_CreateItemHandler, name='create-item'),
    webapp2.Route(r'/get-channel', handler=_GetChannelHandler, name='get-channel'),
    webapp2.Route(r'/add-to-feed/<name>', handler=_AddToChannelHandler, name='add-to-channel'),
], debug=True) #debug=true means stack traces in browser

