""" keyboard events """

import os
import re

import player
from lyrics import debug
from states import state

import app

curses_mapping = {
    'KEY_NPAGE':        '<PageDown>',
    'KEY_PPAGE':        '<PageUp>',
    'KEY_DOWN':         '<Down>',
    'KEY_UP':           '<Up>',
    'KEY_BACKSPACE':    '<BS>',
    'KEY_LEFT':         '<Left>',
    'KEY_RIGHT':        '<Right>',
    'KEY_END':          '<End>',
    'KEY_HOME':         '<Home>',
    '\n':               '<C-J>',
    '\r':               '<Enter>',
    '^[':               '<ESC>',
    ' ':                '<SPACE>',
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


def event_handler(key_str):
    debug.debug('key pressed', repr(key_str))

    # strip ctrl
    #key_chr = curses.ascii.ctrl(key_chr)

    try:
        key_str = curses_mapping[key_str]
    except KeyError:
        if len(key_str) > 1 and key_str[0] == '^':
            key_str = '<C-%s>' % key_str[1:]
        # TODO catch control keys

    debug.debug('key resolved as', key_str)

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
    def got_lyrics(_song, lyrics):
        """:param _song: not a playlist.song, but lyrics.id3.song"""
        if state.playlist.selected._song == _song:
            state.lyrics = lyrics
        app.main_app.draw()

    song = state.playlist.selected
    if song is not None:
        state.lyrics = 'trying to load lyrics.'
        if song in state.fetched_songs:
            state.lyrics = song._lyrics
        else:
            state.fetched_songs.append(song)
            song.get_lyrics_thread(got_lyrics)

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
    if state.split_screen:
        state.current_window = state.window_lyrics

@key('h', '<Left>')
def move_left():
    state.current_window = state.window_song_list

@key('<C-U>', 'u')
def move_half_page_up():
    _move_cursor(y=-int(state.current_window.real_height / 2))

@key('<C-D>', 'd')
def move_half_page_down():
    _move_cursor(y=int(state.current_window.real_height / 2))

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

@key('g', '<Home>')
def move_to_home():
    _move_cursor(y=-state.current_window.cursor_at)

@key('G', '<End>')
def move_to_end():
    y = -state.current_window.cursor_at + state.current_window.get_num_lines()
    _move_cursor(y=y)

@key('H')
def move_to_high():
    w = state.current_window
    y = -w.cursor_at + w.view_at + w.scroll_off
    _move_cursor(y=y)

@key('M')
def move_to_middle():
    w = state.current_window
    y = -w.cursor_at + w.view_at + int(w.real_height / 2)
    _move_cursor(y=y)

@key('L')
def move_to_low():
    w = state.current_window
    y = -w.cursor_at + w.view_at + w.real_height - w.scroll_off - 1
    _move_cursor(y=y)

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

@key(':', '<F2>')
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
    state.playlist.selected = state.playing
    _after_movement()

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
        state.window_song_list.cursor_at = state.playlist.get_selected_index()

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
    state.window_song_list.view_at = 0
    state.window_song_list.cursor_at = 0
    state.playlist.selected = state.playlist.songs[0]

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
