from google.appengine.api import users
import logging

import briefme

import webapp2
import json

import cache
from google.appengine.api import taskqueue

class _GetItemDbpediaResourceHandler(webapp2.RequestHandler):
    def get(self, id):
        #CORS: Allow JSON request from Javascript anywhere
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        url = 'http://dbpedia.org/resource/{}'.format(id)
        result = cache.get_content_for_main_subject(url)
        if result is None:
            taskqueue.add(url        = '/create-item',
                          queue_name = 'addeverything', 
                          params     = {'url': url,
                                        'user_id' : users.get_current_user().user_id(),}

                         )
            self.response.status_int = 204
            return
        if result == "":
            self.response.status_int = 204
            return
        result = json.dumps(result)
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        self.response.write(result)    

class _CreateHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        briefme.brief(self.request.get('url'))
        self.response.write("OK")    

application = webapp2.WSGIApplication([
    webapp2.Route(r'/get-item/dbpedia-resource/<id>', handler=_GetItemDbpediaResourceHandler, name='dbpedia-resource'),
    webapp2.Route(r'/create-item', handler=_CreateHandler, name='create-item'),
], debug=True) #debug=true means stack traces in browser

