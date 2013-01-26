""" keyboard events """

import os
import re
import curses.ascii

import player
from lyrics import debug
from states import state

curses_mapping = {
    curses.KEY_NPAGE:       '<PageDown>',
    curses.KEY_PPAGE:       '<PageUp>',
    curses.KEY_DOWN:        '<Down>',
    curses.KEY_UP:          '<Up>',
    curses.KEY_BACKSPACE:   '<BS>',
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
registered_events = {'normal': {}, 'search': {}}


def key(*keys, **kwargs):
    mode = kwargs.get('mode', 'normal')
    def f(func):
        if mode == 'normal':
            funcs[func] = keys
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        global registered_events
        for k in keys:
            # could check here for default key mappings
            if k.startswith('<'):
                k = k.upper()
            registered_events[mode][k] = wrapper

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


def event_handler(main_app, key_chr):
    debug.debug('key pressed', repr(key_chr))

    # strip ctrl
    #key_chr = curses.ascii.ctrl(key_chr)

    try:
        key_str = curses_mapping[key_chr]
    except KeyError:
        key_str = chr(key_chr)
        # TODO catch control keys

    debug.debug('key pressed', repr(key_chr), key_str)

    if state.search_mode:
        if key_str == '<SPACE>':
            key_str = ' '
        allowed = r'-_ +*/%$&!"\'\?!@`,.;:<>^|#[](){}~='
        if key_str.isalnum() or key_str in allowed:
            _search_write(key_str)
        else:
            try:
                registered_events['search'][key_str](main_app)
            except KeyError:
                pass

    else:
        if state.last_command:
            # cleanup
            state.last_command = ''
            state.keyboard_repeat = ''

        if re.match('\d', key_str):
            state.keyboard_repeat += key_str
        else:
            execute_key_command(main_app, key_str, state.keyboard_repeat)

            state.last_command = key_str

    main_app.draw()


def execute_key_command(main_app, command, repeat):
    try:
        if repeat:
            count = int(repeat)
        else:
            count = 1
        for i in range(count):
            registered_events['normal'][command](main_app)
    except KeyError:
        pass

def start_playing(*args, **kwargs):
    player.play(state.playing.path, lambda: next(*args, **kwargs))

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

@key('.')
def repeat_last_action(main_app):
    for command, repeat in reversed(state.command_list):
        if command != '.':
            break
    if state.command_list:
        execute_key_command(main_app, command, repeat)
        main_app.move_cursor(0, -1)

# ------------------------------------------------------------------------
# gui modifications
# ------------------------------------------------------------------------

@key('<CR>', '<Enter>')
def enter(main_app):
    state.playing = state.playlist.selected
    start_playing(main_app)

@key('s')
def sort(main_app):
    pass

@key('c')
def random(main_app):
    """ random - by chance """
    state.random = not state.random

@key('r')
def repeat(main_app):
    state.repeat = not state.repeat

@key('R')
def repeat_solo(main_app):
    state.repeat_solo = not state.repeat_solo

@key('H', '<F3>')
def help(main_app):
    """help - shows this"""
    state.show_help = not state.show_help

@key('q')
def quit(main_app):
    raise KeyboardInterrupt()

@key('<Esc>')
def cancel_operation(main_app):
    state.show_help = False


# ------------------------------------------------------------------------
# player keys
# ------------------------------------------------------------------------

@key('+', '<C-a>')
def volume_up(main_app):
    player.volume_up()

@key('-', '<C-x>')
def volume_down(main_app):
    player.volume_down()

@key('m')
def mute(main_app):
    player.mute()

@key('<Space>')
def pause(main_app):
    player.pause()

@key('n')
def next(main_app):
    if state.repeat_solo and state.playing is not None:
        p = state.playing
    elif state.random:
        state.random_history_index += 1
        if state.random_history_index >= len(state.random_history):
            p = state.playlist.random(state.playing)
            state.random_history.append(p)
        else:
            p = state.random_history[state.random_history_index]
    else:
        while True:
            p = state.playlist.next(state.playing)
            if p is not None and (p.broken or not os.path.exists(p.path)):
                continue
            break

        if p is None and state.repeat:
            p = state.playlist[0]
    if p:
        state.playing = p
        start_playing(main_app)

@key('N')
def previous(main_app):
    if state.random:
        if state.random_history_index <= 0:
            return

        state.random_history_index -= 1
        p = state.random_history[state.random_history_index]
    else:
        while True:
            p = state.playlist.previous(state.playing)
            if p is not None and (p.broken or not os.path.exists(p.path)):
                continue
            break

        if p is None and state.repeat:
            p = state.playlist[0]
    if p is not None:
        state.playing = p
        start_playing(main_app)

# ------------------------------------------------------------------------
# search
# ------------------------------------------------------------------------

@key('x')
def clear_search(main_app):
    if state.playlist.parent is not None:
        state.playlist = state.playlist.parent

@key('/')
def search(main_app):
    state.search_mode = True
    state.search = ''
    state.search_list.append('')
    state.search_index = len(state.search_list) - 1
    state.search_cursor = 0
    state.playlist = state.playlist.search('')
    debug.debug('base', state.playlist, state.playlist.search('').parent)
    _search_update()

def _search_write(char):
    """No decorator here, because that is handled by the event handler"""
    state.search = state.search[:state.search_cursor] + char \
                    + state.search[state.search_cursor:]
    state.search_cursor += 1
    _search_update()

def _search_update():
    playlist = state.playlist.parent
    for word in re.split('[- _]*', state.search):
        playlist = playlist.search(word)
    state.playlist = playlist

@key('<BS>', mode='search')
def search_backspace(main_app):
    if state.search:
        state.search = state.search[:-1]
        state.search = state.search[:state.search_cursor - 1] \
                        + state.search[state.search_cursor:]
        state.search_cursor -= 1
        _search_update()
    else:
        search_cancel(main_app)

@key('<Enter>', mode='search')
def search_enter(main_app):
    state.search_mode = False
    _search_update()

@key('<Esc>', mode='search')
def search_cancel(main_app):
    if state.search:
        state.search_list[state.search_index] = state.search
    else:
        state.search_list.pop()
    state.search_mode = False
    state.playlist = state.playlist.parent
    #debug.debug('search_list', state.search_list)
    clear_search(main_app)

@key('<Left>', mode='search')
def search_left(main_app):
    state.search_cursor = max(state.search_cursor - 1, 0)

@key('<Right>', mode='search')
def search_right(main_app):
    state.search_cursor = min(state.search_cursor + 1, len(state.search))

@key('<Down>', mode='search')
def search_down(main_app):
    state.search_list[state.search_index] = state.search
    state.search_index = min(state.search_index + 1,
                             len(state.search_list) - 1)
    state.search = state.search_list[state.search_index]
    state.search_cursor = len(state.search)
    _search_update()

@key('<Up>', mode='search')
def search_up(main_app):
    state.search_list[state.search_index] = state.search
    state.search_index = max(state.search_index - 1, 0)
    state.search = state.search_list[state.search_index]
    state.search_cursor = len(state.search)
    _search_update()
