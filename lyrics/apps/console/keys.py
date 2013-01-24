""" keyboard events """

import player

registered_events = {}

curses_mapping = ['']

def key(*keys):
    def f(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        global registered_events
        for k in keys:
            # could check here for default key mappings
            registered_events[k] = wrapper

        wrapper._is_mapping = True
        return wrapper

    return f


def execute_event(app, key_chr):
    try:
        return registered_events[key_chr](app)
    except KeyError:
        pass

# ------------------------------------------------------------------------
# movements
# ------------------------------------------------------------------------

@key('j')
def move_down(app):
    app.move_cursor(1)

@key('k')
def move_up(app):
    app.move_cursor(-1)

@key('l')
def move_right(app):
    app.move_cursor(0, 1)

@key('h')
def move_left(app):
    app.move_cursor(0, -1)

@key('<C-u>')
def move_half_page_up(app):
    app.move_cursor(-int(app.max_list_y / 2))

@key('<C-d>')
def move_half_page_down(app):
    app.move_cursor(int(app.max_list_y / 2))

@key('<C-b>', '<PageUp>')
def move_page_up(app):
    app.move_cursor(app.max_list_y)

@key('<C-f>', '<PageDown>')
def move_page_down(app):
    app.move_cursor(-app.max_list_y)

# ------------------------------------------------------------------------
# player settings
# ------------------------------------------------------------------------

@key('m')
def mute(app):
    player.mute()

@key('<space>')  # space
def pause(app):
    player.pause()

@key('n')
def next(app):
    pass

@key('N')
def previous(app):
    pass

@key('r')
def random(app):
    pass

@key('H', '<F3>')
def help(app):
    """help - shows this"""
    pass

@key('q')
def quit(app):
    raise KeyboardInterrupt()
