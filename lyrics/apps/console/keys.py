""" keyboard events """

from curses import ascii

import player
import debug

registered_events = {}

curses_mapping = {
    'KEY_NPAGE':        '<PageDown>',
    'KEY_PPAGE':        '<PageUp>',
    'KEY_DOWN':         '<Down>',
    'KEY_UP':           '<Up>',
    'KEY_F(1)':         '<F1>',
    'KEY_F(2)':         '<F2>',
    'KEY_F(3)':         '<F3>',
    'KEY_F(4)':         '<F4>',
    'KEY_F(5)':         '<F5>',
    'KEY_F(6)':         '<F6>',
    'KEY_F(7)':         '<F7>',
    'KEY_F(8)':         '<F8>',
    'KEY_F(9)':         '<F9>',
    'KEY_F(10)':        '<F10>',
    'KEY_F(11)':        '<F11>',
    'KEY_F(12)':        '<F12>',
}
for c in curses_mapping:
    curses_mapping[c] = curses_mapping[c].upper()


def key(*keys):
    def f(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        global registered_events
        for k in keys:
            # could check here for default key mappings
            if k.startswith('<'):
                k = k.upper()
            registered_events[k] = wrapper

        wrapper._is_mapping = True
        return wrapper

    return f


def execute_event(app, key_chr):
    debug.debug('key pressed', repr(key_chr))
    if len(key_chr) == 1:
        # strip ctrl
        key_chr = ascii.unctrl(key_chr)
        if key_chr[0] == '^' and len(key_chr) == 2:
            key_chr = '<C-%s>' % key_chr[1]

    try:
        key_chr = curses_mapping[key_chr]
    except KeyError:
        pass
    debug.debug('key pressed', repr(key_chr))

    try:
        return registered_events[key_chr](app)
    except KeyError:
        pass

# ------------------------------------------------------------------------
# movements
# ------------------------------------------------------------------------

@key('j', '<Down>')
def move_down(app):
    app.move_cursor(1)

@key('k', '<Up>')
def move_up(app):
    app.move_cursor(-1)

@key('l')
def move_right(app):
    app.move_cursor(0, 1)

@key('h')
def move_left(app):
    app.move_cursor(0, -1)

@key('<C-U>')
def move_half_page_up(app):
    app.move_cursor(-int(app.max_list_y / 2))

@key('<C-D>')
def move_half_page_down(app):
    app.move_cursor(int(app.max_list_y / 2))

@key('<C-B>', '<PageUp>')
def move_page_up(app):
    app.move_cursor(-app.max_list_y)

@key('<C-F>', '<PageDown>')
def move_page_down(app):
    app.move_cursor(app.max_list_y)

# ------------------------------------------------------------------------
# gui modifications
# ------------------------------------------------------------------------

@key('<CR>', '<Enter>')
def enter(app):
    pass

@key('s')
def sort(app):
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

# ------------------------------------------------------------------------
# player keys
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
