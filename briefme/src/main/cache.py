from google.appengine.api import memcache

def get_content_for_main_subject(uri):
    return memcache.get('content ' + uri)

def set_content_for_main_subject(uri, v):
    memcache.set('content ' + uri, v, 6000)