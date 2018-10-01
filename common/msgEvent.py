# This class is used as a simple event manager so that CM's can 'signal' 
# that a message's signature has been added to the blockchain. 
# This can then trigger an event (in this case a partial function) which
# will do the work of sending the actual message
# An example of how to use this class (with partial functions) is provided below
class MsgEvent(dict):
    def __call__(self, sig,*args,**kwargs):
        self[sig](*args,**kwargs) # Call the partial function
        del self[sig] # Remove it from our events

    def __repr__(self): # not needed but nice for debugging
        return "Events : " + dict.__repr__(self)

    # Overriding this function for a custom error message. Again, not actually required
    def __missing__(self, key):
        print(self.__repr__())
        raise KeyError("Attempt to trigger event for a msg which we have not attempted to append to the blockchain")


# Example usage:
#   >>> from common import msgEvent
#   >>> from functools import partial
#   >>> l = [1,2]
#   >>> append3 = partial(list.append,l,3)
#   >>> appendAny = partial(list.append,l)
#   >>> events = msgEvent.MsgEvent()
#   >>> events['foo'] = append3
#   >>> events['sig'] = appendAny
#   >>> print(events)
#   Events : {'foo': functools.partial(<method 'append' of 'list' objects>, [1, 2], 3), 'sig': functools.partial(<method 'append' of 'list' objects>, [1, 2])}
#   >>> events('foo')
#   >>> print(events)
#   Events : {'sig': functools.partial(<method 'append' of 'list' objects>, [1, 2, 3])}
#   >>> events('sig',9)
#   >>> print(l)
#   [1, 2, 3, 9]


# Heavily inspired by this post: https://stackoverflow.com/a/2022629/7023386