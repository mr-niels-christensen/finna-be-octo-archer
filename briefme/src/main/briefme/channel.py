from google.appengine.ext import ndb
import json

from briefme.item import Item

class Channel(ndb.Model):
    created   = ndb.DateTimeProperty(auto_now_add = True)
    item_keys = ndb.KeyProperty(repeated = True,
                                kind = Item)
    owner     = ndb.UserProperty(required = True)

    @staticmethod
    def for_user(user):
        key = ndb.Key(Channel, user.user_id())
        entity = key.get()
        if entity is None:
            entity = Channel(key = key, owner = user)
        return entity

    def add_item(self, item_key):
        self.item_keys.append(item_key)
        self.put()

    def write_as_json(self, writer):
        d = dict()
        #TODO Get rid of below hacks
        d['item_keys'] = [k.id().split('/')[-1] for k in self.item_keys]
        json.dump(d, writer)
