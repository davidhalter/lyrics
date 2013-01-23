""" keyboard events """

import player

registered_events = {}
def key(*keys):
    def f(func):
        def wrapper():
            func()

        global registered_events
        for k in keys:
            # could check here for default key mappings
            registered_events[k] = wrapper

        wrapper._is_mapping = True
        return wrapper

    return f

def execute_event(key_chr):
    try:
        return registered_events[ord(key_chr)]()
    except KeyError:
        pass

# ------------------------------------------------------------------------
# default key mappings
# ------------------------------------------------------------------------

@key('m')
def mute():
    player.mute()

@key(' ')  # space
def pause():
    player.pause()

@key('n')
def next():
    pass

@key('N')
def next():
    pass

@key('r')
def random():
    pass

@key('h', '<F3>')
def help():
    """help - shows this"""
    pass
