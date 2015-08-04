from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch_errors import DeadlineExceededError

import logging

import rdflib

class UnavailableError(Exception):
    pass

class WebGraph(rdflib.Graph):
    def __init__(self, uri):
        super(WebGraph, self).__init__()
        uri = unicode(uri)
        self.parse(format = 'n3', data = _get_uri(uri))

def _get_uri(uri):
    result = memcache.get('uri ' + uri)
    if result is None:
        result = _load(uri)
        memcache.set('uri ' + uri, result, 86400)
    return result

def _load(uri):
    try:
        response = urlfetch.fetch(uri, headers = {'Accept' : 'text/rdf+n3'})
    except DeadlineExceededError:
        raise UnavailableError('The external database is currently unavailable, deadline exceeded.')
    if response.status_code == 502:
        raise UnavailableError('The external database is currently unavailable, error 502.')
    if response.status_code != 200:
        raise Exception('Some data is currently unavailable, error {}.'.format(response.status_code))
    return response.content
