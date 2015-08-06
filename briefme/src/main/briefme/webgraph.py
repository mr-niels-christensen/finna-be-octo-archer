from google.appengine.api import memcache
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch_errors import DeadlineExceededError

import logging

import rdflib

class UnavailableError(Exception):
    pass

class LargeGraphOrSlowConnectionError(Exception):
    pass

class WebGraph(rdflib.Graph):
    def __init__(self, uri, fail_if_not_loaded = False):
        super(WebGraph, self).__init__()
        uri = unicode(uri)
        try:
            self.parse(format = 'n3', data = _get_uri(uri))
        except LargeGraphOrSlowConnectionError as e:
            if fail_if_not_loaded:
                raise e
            else:
                logging.debug('Large graph or slow connetion for {}'.format(uri), exc_info = True);

def _get_uri(uri):
    result = memcache.get('uri ' + uri)
    if result is None:
        result = _load(uri)
        memcache.set('uri ' + uri, result, 86400)
    return result

def _load(uri):
    try:
        response = urlfetch.fetch(uri, 
                                  headers = {'Accept' : 'text/rdf+n3'},
                                  deadline = 20)
    except DeadlineExceededError:
        raise LargeGraphOrSlowConnectionError('The external database is currently unavailable, deadline exceeded.')
    if response.status_code == 502:
        raise UnavailableError('The external database is currently unavailable, error 502.')
    if response.status_code != 200:
        raise Exception('Some data is currently unavailable, error {}.'.format(response.status_code))
    return response.content
