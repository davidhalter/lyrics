""" keyboard events """

import os
import re
import curses.ascii

import player
from lyrics import debug
from states import state

import app

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


def event_handler(key_chr):
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
                registered_events['search'][key_str]()
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
            execute_key_command(key_str, state.keyboard_repeat)

            state.last_command = key_str

    app.main_app.draw()


def execute_key_command(command, repeat):
    try:
        if repeat:
            count = int(repeat)
        else:
            count = 1
        for i in range(count):
            registered_events['normal'][command]()
    except KeyError:
        pass

def _start_playing():
    player.play(state.playing.path, lambda: next())
    _after_movement()

# ------------------------------------------------------------------------
# movements
# ------------------------------------------------------------------------

def _after_movement():
    pass

def _move_cursor(x=0, y=0):
    state.current_window.move_cursor(x, y)
    _after_movement()

@key('j', '<Down>')
def move_down():
    _move_cursor(y=1)

@key('k', '<Up>')
def move_up():
    _move_cursor(y=-1)

@key('l', '<Right>')
def move_right():
    _move_cursor(x=1)

@key('h', '<Left>')
def move_left():
    _move_cursor(x=-1)

@key('<C-U>', 'u')
def move_half_page_up():
    _move_cursor(y=-int(state.current_window.height / 2))

@key('<C-D>', 'd')
def move_half_page_down():
    _move_cursor(y=int(state.current_window.height / 2))

@key('<C-B>', '<PageUp>')
def move_page_up():
    _move_cursor(y=-state.current_window.height)

@key('<C-F>', '<PageDown>')
def move_page_down():
    _move_cursor(y=state.current_window.height)

@key('.')
def repeat_last_action():
    for command, repeat in reversed(state.command_list):
        if command != '.':
            break
    if state.command_list:
        execute_key_command(command, repeat)

# ------------------------------------------------------------------------
# gui modifications
# ------------------------------------------------------------------------

@key('<CR>', '<Enter>')
def enter():
    state.playing = state.playlist.selected
    _start_playing()

@key('s')
def sort():
    pass
    _after_movement()

@key('r')
def random():
    state.random = not state.random

@key('i')
def repeat():
    """repeat = iterate"""
    state.repeat = not state.repeat

@key('I')
def repeat_solo():
    """repeat solo - iterate solo"""
    state.repeat_solo = not state.repeat_solo

@key('H', '<F3>')
def help():
    """help - shows this"""
    state.show_help = not state.show_help

@key('q')
def quit():
    raise KeyboardInterrupt()

@key('<Esc>')
def cancel_operation():
    state.show_help = False


# ------------------------------------------------------------------------
# player keys
# ------------------------------------------------------------------------
def _switch_song():
    pass

@key('+', '<C-a>')
def volume_up():
    player.volume_up()

@key('-', '<C-x>')
def volume_down():
    player.volume_down()

@key('m')
def mute():
    player.mute()

@key('<Space>')
def pause():
    player.pause()

@key('n')
def next():
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
        _start_playing()
    _switch_song()
    app.main_app.draw()

@key('N')
def previous():
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
        _start_playing()
    _switch_song()

# ------------------------------------------------------------------------
# search
# ------------------------------------------------------------------------

@key('x')
def clear_search():
    if state.playlist.parent is not None:
        state.playlist = state.playlist.parent

@key('/')
def search():
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
    _after_movement()

@key('<BS>', mode='search')
def search_backspace():
    if state.search:
        state.search = state.search[:-1]
        state.search = state.search[:state.search_cursor - 1] \
                        + state.search[state.search_cursor:]
        state.search_cursor -= 1
        _search_update()
    else:
        search_cancel()

@key('<Enter>', mode='search')
def search_enter():
    state.search_mode = False
    _search_update()

@key('<Esc>', mode='search')
def search_cancel():
    if state.search:
        state.search_list[state.search_index] = state.search
    else:
        state.search_list.pop()
    state.search_mode = False
    state.playlist = state.playlist.parent
    #debug.debug('search_list', state.search_list)
    clear_search()

@key('<Left>', mode='search')
def search_left():
    state.search_cursor = max(state.search_cursor - 1, 0)

@key('<Right>', mode='search')
def search_right():
    state.search_cursor = min(state.search_cursor + 1, len(state.search))

@key('<Down>', mode='search')
def search_down():
    state.search_list[state.search_index] = state.search
    state.search_index = min(state.search_index + 1,
                             len(state.search_list) - 1)
    state.search = state.search_list[state.search_index]
    state.search_cursor = len(state.search)
    _search_update()

@key('<Up>', mode='search')
def search_up():
    state.search_list[state.search_index] = state.search
    state.search_index = max(state.search_index - 1, 0)
    state.search = state.search_list[state.search_index]
    state.search_cursor = len(state.search)
    _search_update()
