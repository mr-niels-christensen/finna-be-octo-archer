from google.appengine.api import memcache
from urllib2 import urlopen, Request
from google.appengine.api import urlfetch
import logging

def get_uri(uri):
    uri = unicode(uri)
    result = memcache.get('zuri ' + uri)
    if result is None:
        result = _load(uri)
        memcache.set('zuri ' + uri, result, 86400)
    return result

_ACCEPT = 'text/rdf+n3;q=0.9,application/xhtml+xml;q=0.5, */*;q=0.1'

def _load(uri):
    response = urlfetch.fetch(uri, headers = {'Accept' : _ACCEPT})
    return response.content
