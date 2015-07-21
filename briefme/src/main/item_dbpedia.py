import cache
import json
from google.appengine.api import taskqueue
import logging

class ItemDbpediaResource(object):
    def __init__(self, id):
        self._id = id
        self._url = 'http://dbpedia.org/resource/{}'.format(id)

    def create(self, user_id):
        taskqueue.add(url = '/create-item',
              queue_name = 'addeverything', 
              params     = {'url': self._url,
                            'user_id' : user_id,}
             )

    def is_ready(self):
        result = cache.get_content_for_main_subject(self._url)
        if result is None:
            return False
        if result is "":
            return False
        return True

    def is_in_progress(self):
        result = cache.get_content_for_main_subject(self._url)
        if result is None:
            return False
        if result is "":
            return True
        return False

    def write_as_json(self, writer):
        assert self.is_ready()
        result = cache.get_content_for_main_subject(self._url)
        result = json.dumps(result)
        writer.write(result)
