from google.appengine.api import memcache
from urllib2 import urlopen, Request

def get_content_for_main_subject(uri):
    return memcache.get('content ' + uri)

def set_content_for_main_subject(uri, v):
    memcache.set('content ' + uri, v, 6000)

def get_uri(uri):
    result = memcache.get('uri ' + uri)
    if result is None:
        result = _load(uri)
        memcache.set('uri ' + uri, result, 86400)
    return result

def _load(uri):
    myheaders = dict()
    myheaders['Accept'] = (
        'application/rdf+xml,text/rdf+n3;q=0.9,' +
        'application/xhtml+xml;q=0.5, */*;q=0.1')
    req = Request(unicode(uri), None, myheaders)
    file = urlopen(req)
    return file.read()
