from google.appengine.api import users
import logging

import briefme

import webapp2
import json

import cache
from item_dbpedia import ItemDbpediaResource
from uuid import uuid4

class _GetItemDbpediaResourceHandler(webapp2.RequestHandler):
    def get(self, id):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        uuid = uuid4()
        logging.debug('BEGIN request {} for {}'.format(uuid, id))
        item = ItemDbpediaResource(id)
        if item.is_ready():
            logging.debug('END request {} for {}, was ready'.format(uuid, id))
            self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
            item.write_as_json(self.response)
            return
        if item.is_in_progress():
            logging.debug('END request {} for {}, task in progess'.format(uuid, id))
            self.response.status_int = 204
            return
        item.create(users.get_current_user().user_id())
        logging.debug('END request {} for {}, task requested'.format(uuid, id))
        self.response.status_int = 204
        return

class _CreateHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        briefme.brief(self.request.get('url'))
        self.response.write("OK")    

application = webapp2.WSGIApplication([
    webapp2.Route(r'/get-item/dbpedia-resource/<id>', handler=_GetItemDbpediaResourceHandler, name='dbpedia-resource'),
    webapp2.Route(r'/create-item', handler=_CreateHandler, name='create-item'),
], debug=True) #debug=true means stack traces in browser

