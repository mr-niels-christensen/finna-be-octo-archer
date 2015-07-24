from google.appengine.api import users
import logging

import briefme

import webapp2
import json

import cache
from item_dbpedia import ItemDbpediaResource
from feed import Feed

class _GetItemDbpediaResourceHandler(webapp2.RequestHandler):
    def get(self, id):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        item = ItemDbpediaResource(id, users.get_current_user().user_id())
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        item.write_as_json(self.response)
        return

class _GetMetaItemDbpediaResourceHandler(webapp2.RequestHandler):
    def get(self, id):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        item = ItemDbpediaResource(id, users.get_current_user().user_id())
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        item.write_as_json(self.response, meta_only = True)
        return

class _CreateHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        item = ItemDbpediaResource.from_request(self.request)
        try:
            briefme.brief(item)
        except Exception as e:
            logging.warn('Failed to process {}'.format(item), exc_info = True);
            item.set_failed(e)
        self.response.write("OK")  
        return

class _GetFeedHandler(webapp2.RequestHandler):
    def get(self):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        feed = Feed(users.get_current_user().user_id())
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        feed.write_as_json(self.response)
        return

class _AddToFeedHandler(webapp2.RequestHandler):
    def post(self, id):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        feed = Feed(users.get_current_user().user_id())
        item = ItemDbpediaResource(id, users.get_current_user().user_id())
        feed.add_item(id)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        item.write_as_json(self.response)
        return

application = webapp2.WSGIApplication([
    webapp2.Route(r'/get-item/dbpedia-resource/<id>', handler=_GetItemDbpediaResourceHandler, name='dbpedia-resource'),
    webapp2.Route(r'/get-meta-item/dbpedia-resource/<id>', handler=_GetMetaItemDbpediaResourceHandler, name='dbpedia-resource'),
    webapp2.Route(r'/create-item', handler=_CreateHandler, name='create-item'),
    webapp2.Route(r'/get-feed', handler=_GetFeedHandler, name='get-feed'),
    webapp2.Route(r'/add-to-feed/<id>', handler=_AddToFeedHandler, name='add-to-feed'),
], debug=True) #debug=true means stack traces in browser

