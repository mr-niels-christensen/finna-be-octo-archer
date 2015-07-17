from google.appengine.api import users
import logging

import selectresource
import briefme

import webapp2
import json

import cache
from google.appengine.api import taskqueue

def content_route():
    return webapp2.Route(r'/content', handler=_ContentHandler, name='content')

def add_route():
    return webapp2.Route(r'/add', handler=_AddHandler, name='add')

class _ContentHandler(webapp2.RequestHandler):
    def get(self):
        #Access-Control-Allow-Origin: *
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        result = cache.get_content_for_main_subject(self.request.get('iri'))
        if result is None:
            taskqueue.add(url        = '/add',
                          queue_name = 'addeverything', 
                          params     = {'iri': self.request.get('iri')})
            result = "Task spawned"
        result = json.dumps(result)
        self.response.write(result)    

class _AddHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        briefme.brief(self.request.get('iri'))
        self.response.write("OK")    

class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            if users.is_current_user_admin():
                self.response.out.write(
                    'Hi Admin'
                )
            else:
                self.response.out.write(
                    'Hi non-admin {}. Nothing to see here.'.format(user.nickname())
                )
        else:
            self.redirect(users.create_login_url(self.request.uri))

application = webapp2.WSGIApplication([
    content_route(),
    add_route(),
], debug=True) #debug=true means stack traces in browserapplication = webapp.WSGIApplication([('/', MainPage), ('/_ah/xmpp/message/chat/', ChatReceiver)], debug=True)
