import json
from google.appengine.api import taskqueue
from google.appengine.api import memcache
import logging

_INITIAL_STATE = {'ready' : False,
                  'progress' : 0, }

class ItemDbpediaResource(object):
    def __init__(self, id, user_id):
        self._id = id
        self._user_id = user_id
        if memcache.get(self._id) is None:
            self._create()

    @staticmethod
    def from_request(request):
        return ItemDbpediaResource(request.get('id'), request.get('user_id'))
        
    def external_url(self):
        return 'http://dbpedia.org/resource/{}'.format(self._id)

    def _create(self):
        memcache.set(self._id, _INITIAL_STATE, 6000)
        taskqueue.add(url = '/create-item',
              queue_name = 'addeverything', 
              params     = {'id': self._id,
                            'user_id' : self._user_id,}
             )

    def write_as_json(self, writer):
        result = memcache.get(self._id)
        result = json.dumps(result)
        writer.write(result)

    def set_progress(self, progress):
        state = memcache.get(self._id)
        state['progress'] = progress
        memcache.set(self._id, state, 6000)

    def set_data(self, data):
        state = memcache.get(self._id)
        state['ready'] = True
        del state['progress']
        state['data'] = data
        memcache.set(self._id, state, 6000)

    def __str__(self):
        return self._id
