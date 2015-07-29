from google.appengine.api import users
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import logging
import webapp2
import json

from briefme import analyse
from briefme import cache
from briefme.channel import Channel
from briefme.item import Item

def _task(key):
    taskqueue.add(url        = '/create-item',
                  queue_name = 'addeverything', 
                  params     = {'key_urlsafe': key.urlsafe()}
    )

class _GetItemDbpediaResourceHandler(webapp2.RequestHandler):
    def get(self, id):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        item = Item.for_name(id, create_cb = _task)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        item.write_as_json(self.response)
        return

class _CreateHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        item = Item.for_key_urlsafe(self.request.get('key_urlsafe'))
        try:
            analyse.brief(item)
        except Exception as e:
            logging.warn('Failed to process {}'.format(item), exc_info = True);
            item.set_failed(e)
        self.response.write("OK")  
        return

class _GetFeedHandler(webapp2.RequestHandler):
    def get(self):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        channel = Channel.for_user(users.get_current_user())
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        channel.write_as_json(self.response)
        return

class _AddToFeedHandler(webapp2.RequestHandler):
    def post(self, id):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        channel = Channel.for_user(users.get_current_user())
        item = Item.for_name(id, create_cb = _task)
        channel.add_item(item.key)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        item.write_as_json(self.response)
        return

application = webapp2.WSGIApplication([
    webapp2.Route(r'/get-item/dbpedia-resource/<id>', handler=_GetItemDbpediaResourceHandler, name='dbpedia-resource'),
    webapp2.Route(r'/get-meta-item/dbpedia-resource/<id>', handler=_GetItemDbpediaResourceHandler, name='dbpedia-resource'),
    webapp2.Route(r'/create-item', handler=_CreateHandler, name='create-item'),
    webapp2.Route(r'/get-feed', handler=_GetFeedHandler, name='get-feed'),
    webapp2.Route(r'/add-to-feed/<id>', handler=_AddToFeedHandler, name='add-to-feed'),
], debug=True) #debug=true means stack traces in browser

