from google.appengine.ext import ndb
import json

from briefme.item import Item

class _ItemInChannel(ndb.Model):
    key  = ndb.KeyProperty(required = True,
                           kind = Item)
    done = ndb.BooleanProperty(required = True,
                               default = False)
    checkpoint = ndb.IntegerProperty(required = True,
                                     default = -1)

class Channel(ndb.Model):
    '''This represents an RSS-like channel, as in a podcast series.
       In the current model, there is exactly one channel per user.
       The channel simply records the items (think of these as "single posts")
       that the user has added to her Channel.
    '''

    created   = ndb.DateTimeProperty(auto_now_add = True)

    '''The NDB keys for not-done items in this Channel.
    '''
    items     = ndb.LocalStructuredProperty(_ItemInChannel, repeated=True)

    '''The NDB keys for done items in this Channel.
    '''
    done_keys = ndb.KeyProperty(repeated = True,
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
        self.items.append(_ItemInChannel(key = item_key))
        self.put()

    def mark_item_done(self, item_key):
        '''Moves item_key from self.item_keys to self.done_keys
           @param item_key: An ndb.Key for an Item in self.item_keys
        '''
        for iic in self.items:
            if iic.key == item_key:
                iic.done = True
        self.put()

    def set_checkpoint(self, item_key, index):
        '''TODO
           @param item_key: An ndb.Key for an Item in self.item_keys
        '''
        for iic in self.items:
            if iic.key == item_key:
                iic.checkpoint = index
        self.put()

    def write_as_json(self, writer):
        '''Writes this Channel to the given writer as JSON.
           Right now, this writes a JSON list with one element per item.
        '''
        l = [i.as_jsonifiable() for i in ndb.get_multi([iic.key for iic in self.items if not iic.done])]
        json.dump(l, writer)
