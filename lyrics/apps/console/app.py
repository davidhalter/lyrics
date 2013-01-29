""" the curses implementation """

import curses
from threading import Lock

import keys
from lyrics import debug
import player
from states import state


class Window(object):
    def __init__(self, x, y, width, height):
        #debug.debug('new_win', self.__class__.__name__, x, y, width, height)
        self.win_curses = curses.newwin(height, width, y, x)
        self.height, self.width = self.win_curses.getmaxyx()
        self.init()
        self.draw()

    def init(self):
        pass

    def draw(self):
        pass

    def add_str(self, x, y, string, col=None, align='left'):
        x, y = self.clean_position(x, y)
        if align == 'right':
            x = max(0, x - len(string))

        # check for strings that are being written in the wrong place.
        if y >= self.height:
            debug.debug('cannot write here: y=%s' % y)
            return False
        result = True
        if x + len(string) >= self.width:
            debug.debug('cannot write here: x=%s, len=%s' % (x, len(string)))
            string = string[:self.width - x - 1]
            result = False

        string = string.replace('\0', '')
        self.win_curses.addstr(y, x, string.encode('UTF-8'), col)
        return result

    def clean_position(self, x, y):
        width, height = self.width, self.height
        if isinstance(x, float):
            x = int(width * x)
        if isinstance(y, float):
            y = int(height * y)

        if x is None:
            x = width
        if y is None:
            y = height

        if x < 0:
            x = width + x
        if y < 0:
            y = height + y
        return x, y


class NavigableWindow(Window):
    def __init__(self, x, y, width, height, border=2):
        self.view_at = 0
        self.cursor_at = 0
        self.border = 0
        self.scrolloff = 5  # keep at least 5 lines above/below cursor

        self._real_height = height - border
        super(NavigableWindow, self).__init__(x, y, width, height)

    def move_cursor(self, x, y):
        """ x can always be ignored, it's just about the y movement """
        num_lines = self.get_num_lines()
        debug.debug('n', num_lines)
        self.cursor_at = min(max(self.view_at, 0), num_lines - 1)

        max_view_top = self.cursor_at + self.scrolloff
        max_view_bottom = self.cursor_at + self._real_height - self.scrolloff
        if self.view_at < max_view_top:
            self.view_at = max(0, max_view_top)
        elif self.view_at > max_view_bottom:
            self.view_at = min(max_view_bottom,
                                num_lines - self._real_height - 1)

    def visible_in_window(self):
        """ return the two coordinates of the start and the end window """
        return self.view_at, self.view_at + self._real_height

    def get_num_lines(self):
        raise NotImplementedError()


class App(Window):
    def __init__(self):
        # need to override the default __init__
        self.draw_lock = Lock()

    def start(self):
        curses.wrapper(self.setup)  # the infinite loop

    def setup(self, stdscr):
        self.win_curses = stdscr

        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(8, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_GREEN)

        self.win_curses.nodelay(0)
        self.draw()

        keys._after_movement()

        self.run()

    def run(self):
        while True:
            try:
                c = self.head.win_curses.getch()
                if c == curses.KEY_RESIZE:
                    self.draw()
                    continue
                keys.event_handler(c)
            except KeyboardInterrupt:
                # doesn't work with ctrl c: http://bugs.python.org/issue1687125
                break

        # cleanup
        player.close()

    def create_window(self, cls, x, y, width, height):
        x, y = self.clean_position(x, y)
        width, height = self.clean_position(width, height)
        return cls(x, y, width, height)

    def draw(self):
        self.draw_lock.acquire()
        self.height, self.width = self.win_curses.getmaxyx()
        self.head = self.create_window(Head, 0, 0, None, 1)
        if state.split_screen:
            golden = 0.382
            self.song_list = self.create_window(SongList, 0, 1, golden, -3)
            self.lyrics = self.create_window(Lyrics, golden, 1, 1 - golden, -3)
        else:
            self.song_list = self.create_window(SongList, 0, 1, None, -3)
        self.status_line = self.create_window(StatusLine, 0, -2, None, 1)
        self.footer = self.create_window(Footer, 0, -1, None, 1)
        state.current_window = self.song_list

        # setup cursor
        if state.search_mode:
            curses.setsyx(0, state.search_cursor + 1)
        try:
            curses.curs_set(2 if state.search_mode else 0)
        except:
            pass

        curses.doupdate()
        self.draw_lock.release()


class Head(Window):
    def init(self):
        if state.search_mode:
            info = '/' + state.search
        else:
            info = "lyrics - press H for help."
        self.add_str(0, 0, info, curses.color_pair(4))
        self.win_curses.bkgd(' ', curses.color_pair(7))
        self.win_curses.noutrefresh()
        self.win_curses.keypad(1)  # because it does the key handling


class Footer(Window):
    def init(self):
        self.win_curses.bkgd(' ')
        last = state.keyboard_repeat + state.last_command
        self.add_str(-5, 0, last, curses.color_pair(2), align='right')
        self.win_curses.noutrefresh()


class StatusLine(Window):
    def init(self):
        self.win_curses.bkgd(' ', curses.color_pair(7))

        r = 'repeat' if state.repeat else 'solo' if state.repeat_solo \
                                                        else 'no-repeat'
        status = "[%s, %s]" % (r, 'random' if state.random else 'no-random')
        self.add_str(-1, 0, status, curses.color_pair(2), align='right')

        if state.playing is not None:
            length = self.width - 2 - len(status)
            col = curses.color_pair(7)
            self.add_str(0, 0, state.playing.format(length, album=True), col)

        self.win_curses.bkgd(' ', curses.color_pair(7))
        self.win_curses.noutrefresh()


class Lyrics(Window):
    def init(self):
        self.win_curses.noutrefresh()

    def draw(self):
        self.win_curses.erase()
        #self.win_curses.box()

        length, max_display = self.clean_position(-2, -2)

        col = curses.color_pair(1)
        if state.show_help:
            txt = "Help\n" + keys.help_documentation()
            txt += "\nWritten by David Halter -> http://jedidjah.ch"
        else:
            txt = state.lyrics

        for i, line in enumerate(txt.splitlines()):
            self.add_str(1, i + 1, line, col)

        self.win_curses.bkgd(' ')
        self.win_curses.refresh()


class SongList(NavigableWindow):
    def init(self):
        self.win_curses.noutrefresh()

    def draw(self):
        self.win_curses.erase()
        self.win_curses.box()
        self.win_curses.bkgd(' ')

        length, max_display = self.clean_position(-2, -2)
        playlist = state.playlist
        _range = range(*self.visible_in_window())
        for i, song_nr in enumerate(_range):
            song = playlist[song_nr]
            if song == state.playing and song == playlist.selected:
                col = curses.color_pair(9)
            elif song == playlist.selected:
                col = curses.color_pair(6)
            elif song == state.playing:
                col = curses.color_pair(4)
            else:
                col = curses.color_pair(5)

            if song == state.playing or song == playlist.selected:
                self.win_curses.hline(i + 1, 1, ' ', length, col)

            self.add_str(1, i + 1, song.format(length), col)

        self.win_curses.refresh()

    def move_cursor(self, x, y):
        super(SongList, self).move_cursor(x, y)
        state.playlist.selected = state.playlist[self.cursor_at]

    def get_num_lines(self):
        return len(state.playlist.songs)

main_app = App()
