""" keyboard events """

import curses.ascii

import player
import debug
from states import state

registered_events = {}

curses_mapping = {
    curses.KEY_NPAGE:       '<PageDown>',
    curses.KEY_PPAGE:       '<PageUp>',
    curses.KEY_DOWN:        '<Down>',
    curses.KEY_UP:          '<Up>',
    curses.KEY_LEFT:        '<Left>',
    curses.KEY_RIGHT:       '<Right>',
    curses.ascii.NL:        '<Enter>',
    curses.ascii.ESC:       '<ESC>',
    curses.ascii.SP:        '<SPACE>',
    curses.KEY_F1:          '<F1>',
    curses.KEY_F2:          '<F2>',
    curses.KEY_F3:          '<F3>',
    curses.KEY_F4:          '<F4>',
    curses.KEY_F5:          '<F5>',
    curses.KEY_F6:          '<F6>',
    curses.KEY_F7:          '<F7>',
    curses.KEY_F8:          '<F8>',
    curses.KEY_F9:          '<F9>',
    curses.KEY_F10:         '<F10>',
    curses.KEY_F11:         '<F11>',
    curses.KEY_F12:         '<F12>',
}
for c in curses_mapping:
    curses_mapping[c] = curses_mapping[c].upper()

funcs = {}


def key(*keys):
    def f(func):
        funcs[func] = keys
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


def help_documentation():
    """ returns a string with the definitions of the keys """
    s = ''
    for f, keys in funcs.items():
        k = '  ' + ' '.join(keys)
        tabs = int(3 - len(k)/8) * '\t'
        s += '%s%s%s\n' % (k, tabs, f.__doc__ or f.__name__.replace('_', ' '))
    return s


def execute_event(app, key_chr):
    debug.debug('key pressed', repr(key_chr))

    # strip ctrl
    #key_chr = curses.ascii.ctrl(key_chr)

    try:
        key_str = curses_mapping[key_chr]
    except KeyError:
        key_str = chr(key_chr)
    debug.debug('key pressed', repr(key_chr), key_str)

    try:
        return registered_events[key_str](app)
    except KeyError:
        pass

# ------------------------------------------------------------------------
# movements
# ------------------------------------------------------------------------

@key('j', '<Down>')
def move_down(main_app):
    main_app.move_cursor(1)

@key('k', '<Up>')
def move_up(main_app):
    main_app.move_cursor(-1)

@key('l', '<Right>')
def move_right(main_app):
    main_app.move_cursor(0, 1)

@key('h', '<Left>')
def move_left(main_app):
    main_app.move_cursor(0, -1)

@key('<C-U>', 'u')
def move_half_page_up(main_app):
    main_app.move_cursor(-int(state.current_window.height / 2))

@key('<C-D>', 'd')
def move_half_page_down(main_app):
    main_app.move_cursor(int(state.current_window.height / 2))

@key('<C-B>', '<PageUp>')
def move_page_up(main_app):
    main_app.move_cursor(-state.current_window.height)

@key('<C-F>', '<PageDown>')
def move_page_down(main_app):
    main_app.move_cursor(state.current_window.height)

# ------------------------------------------------------------------------
# gui modifications
# ------------------------------------------------------------------------

@key('<CR>', '<Enter>', '<C-J>')
def enter(main_app):
    player.play(state.playlist.selected.path, lambda: next(main_app))

@key('s')
def sort(main_app):
    pass

@key('r')
def random(main_app):
    pass

@key('H', '<F3>')
def help(main_app):
    """help - shows this"""
    state.show_help = not state.show_help
    main_app.draw()

@key('q')
def quit(main_app):
    raise KeyboardInterrupt()

# ------------------------------------------------------------------------
# player keys
# ------------------------------------------------------------------------

@key('m')
def mute(main_app):
    player.mute()

@key('<space>', 'p')  # space
def pause(main_app):
    player.pause()

@key('n')
def next(main_app):
    pass

@key('N')
def previous(main_app):
    pass
