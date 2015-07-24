from google.appengine.api import memcache
import logging
import json

_INITIAL_STATE = {'past' : [],
                  'future' : []}

class Feed(object):
    def __init__(self, user_id):
        self._user_id = user_id
        if memcache.get(self._user_id) is None:
            self._create()

    def _create(self):
        memcache.set(self._user_id, _INITIAL_STATE, 6000)

    def add_item(self, id):
        state = memcache.get(self._user_id)
        state['future'].append(id)
        memcache.set(self._user_id, state, 6000)

    def mark_seen(self, id):
        state = memcache.get(self._user_id)
        state['future'].remove(id)
        state['past'].append(id)
        memcache.set(self._user_id, state, 6000)

    def write_as_json(self, writer, meta_only = False):
        result = memcache.get(self._user_id)
        result['user_id'] = self._user_id
        result = json.dumps(result)
        writer.write(result)

