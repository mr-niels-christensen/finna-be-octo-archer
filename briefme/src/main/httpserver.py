from google.appengine.api import users
import logging

import selectresource
import briefme

import webapp2
import json

def lookup_route():
    return webapp2.Route(r'/lookup/<phrase>', handler=_LookupHandler, name='lookup')

def content_route():
    return webapp2.Route(r'/content', handler=_ContentHandler, name='content')

class _LookupHandler(webapp2.RequestHandler):
    def get(self, phrase):
        #Access-Control-Allow-Origin: *
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        result = selectresource.lookup(phrase)
        result = json.dumps(result)
        self.response.write(result)    

class _ContentHandler(webapp2.RequestHandler):
    def get(self):
        #Access-Control-Allow-Origin: *
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
        result = briefme.brief(self.request.get('iri'))
        result = json.dumps(result)
        self.response.write(result)    

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
    lookup_route(),
    content_route(),
], debug=True) #debug=true means stack traces in browserapplication = webapp.WSGIApplication([('/', MainPage), ('/_ah/xmpp/message/chat/', ChatReceiver)], debug=True)
