from google.appengine.ext import ndb
import json

from briefme.item import Item

class Channel(ndb.Model):
    '''This represents an RSS-like channel, as in a podcast series.
       In the current model, there is exactly one channel per user.
       The channel simply records the items (think of these as "single posts")
       that the user has added to her Channel.
       An obvious TODO is to mark the items that have alreaddy been played.
    '''

    created   = ndb.DateTimeProperty(auto_now_add = True)

    '''The NDB keys for the items in this Channel.
    '''
    item_keys = ndb.KeyProperty(repeated = True,
                                kind = Item)
    owner     = ndb.UserProperty(required = True)

    @staticmethod
    def for_user(user):
        '''Looks up the Channel for the given user.
           If the user has no Channel, a new one is created
           but not stored.
           @param user: A GAE User instance
           @return A Channel instance. Never returns None.
        '''
        key = ndb.Key(Channel, user.user_id())
        entity = key.get()
        if entity is None:
            entity = Channel(key = key, owner = user)
        return entity

    def add_item(self, item_key):
        '''Adds one Item to this Channel, then stores this Channel.
           @param item_key: An ndb.Key for an Item to add
        '''
        self.item_keys.append(item_key)
        self.put()

    def write_as_json(self, writer):
        '''Writes this Channel to the given writer as JSON.
           Right now, this writes a JSON list with one element per item.
        '''
        l = [i.as_jsonifiable() for i in ndb.get_multi(self.item_keys)]
        json.dump(l, writer)
