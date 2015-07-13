from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import xmpp
import time
import logging

import selectresource
import briefme

class MainPage(webapp.RequestHandler):
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

def _src_dest_body(message):
    return (message.sender.split('/')[0],
            message.to,
            message.body.encode('utf-8','ignore'))

class ChatReceiver(webapp.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        src, dest, body = _src_dest_body(message)
        trimmed_body = body.strip()#.lower()#.translate(None, '?!.,;:-')
        logging.info("From <{}> to {}: <{}> -> <{}>".format(src, dest, body, trimmed_body))
        respond(src, trimmed_body, Responder(message))
        
class Responder():
    def __init__(self, message):
        self._message = message
        self._buffer = ''
        
    def write(self, text):
        text = self._buffer + text
        for raw_line in text.split('\n')[:-1]:
            line = raw_line.strip()
            if len(line) > 0:
                self._send(line)
        self._buffer = text.split('\n')[-1]
    
    def writeln(self, text):
        text = self._buffer + text
        for raw_line in text.split('\n'):
            line = raw_line.strip()
            if len(line) > 0:
                self._send(line)
        self._buffer = ''
    
    def _send(self, line):
        #time.sleep(float(len(line)) / 50)
        #logging.info("To <{orig[0]}> from {orig[1]}: <{line}>".format(line = line, orig = _src_dest_body(self._message)))
        self._message.reply(line)

def respond(sender, trimmed_body, responder):
    if trimmed_body.startswith('http'):
        briefme.brief(trimmed_body, responder)
    else:
        selectresource.lookup(trimmed_body, responder)

application = webapp.WSGIApplication([('/', MainPage), ('/_ah/xmpp/message/chat/', ChatReceiver)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
