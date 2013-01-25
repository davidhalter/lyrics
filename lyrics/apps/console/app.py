""" the curses implementation """

import curses

import lyrics
import playlist
import keys
import debug
import player


class States(object):
    """State machine of the app"""
    def __init__(self, playlist):
        self.playlist = playlist

        self.split_screen = False
        self._show_help = False
        self.playing = None
        self.current_window = None
        self._show_lyrics = False

    @property
    def show_help(self):
        return self._show_help

    @show_help.setter
    def show_help(self, value):
        if value:
            self.split_screen = True
        else:
            self.split_screen = self.show_lyrics
        self._show_help = value

    @property
    def show_lyrics(self):
        return self._show_lyrics

    @show_lyrics.setter
    def show_lyrics(self, value):
        if value:
            self.split_screen = True
        self._show_lyrics = value


class Window(object):
    def __init__(self, states, x, y, width, height):
        debug.debug('new_win', self.__class__.__name__, x, y, width, height)

        self.states = states
        self.win_curses = curses.newwin(height, width, y, x)
        self.height, self.width = self.win_curses.getmaxyx()
        self.init()
        self.draw()

    def init(self):
        pass

    def draw(self):
        pass

    def add_str(self, x, y, string, col=None):
        self.win_curses.addstr(y, x, string, col)

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


class App(Window):
    def __init__(self, path):
        p = playlist.Playlist.from_path(path)
        self.states = States(p)

    def start(self):
        curses.wrapper(self.setup)  # the infinite loop

    def setup(self, stdscr):
        self.win_curses = stdscr
        self.height, self.width = self.win_curses.getmaxyx()
        try:
            curses.curs_set(0)
        except:
            pass

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

        self.run()

    def run(self):
        while True:
            try:
                c = self.head.win_curses.getch()
                if c == curses.KEY_RESIZE:
                    self.draw()
                    continue
                keys.execute_event(self, c)
            except KeyboardInterrupt:
                # doesn't work with ctrl c: http://bugs.python.org/issue1687125
                break

        # cleanup
        player.close()

    def create_window(self, cls, x, y , width, height):
        x, y = self.clean_position(x, y)
        width, height = self.clean_position(width, height)
        return cls(self.states, x, y, width, height)

    def move_cursor(self, y, x=0):
        return self.states.current_window.move_cursor(y, x)

    def draw(self):
        self.head = self.create_window(Head, 0, 0, None, 1)
        if self.states.split_screen:
            golden = 0.382
            self.song_list = self.create_window(SongList, 0, 1, golden, -3)
            self.lyrics = self.create_window(Lyrics, golden, 1, 1 - golden, -3)
        else:
            self.song_list = self.create_window(SongList, 0, 1, None, -3)
        self.status_line = self.create_window(StatusLine, 0, -2, None, 1)
        self.footer = self.create_window(Footer, 0, -1, None, 1)
        self.states.current_window = self.song_list

        curses.doupdate()


class Head(Window):
    def init(self):
        info = " lyrics - press H for help."
        self.win_curses.addstr(0, 0, info, curses.color_pair(4))
        right_str = "test"
        x, y = self.clean_position(- len(right_str) - 1, 0)
        self.win_curses.addstr(y, x, right_str, curses.color_pair(2))
        self.win_curses.bkgd(' ', curses.color_pair(7))
        self.win_curses.noutrefresh()
        self.win_curses.keypad(1)  # because it does the key handling


class Footer(Window):
    def init(self):
        #self.win_curses.bkgd(' ', curses.color_pair(7))
        self.win_curses.noutrefresh()


class StatusLine(Window):
    def init(self):
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
        if self.states.show_help:
            txt = "Help\n" + keys.help_documentation()
            txt += "\nWritten by David Halter -> http://jedidjah.ch"
        else:
            txt = ""

        for i, line in enumerate(txt.splitlines()):
            self.add_str(1, i + 1, line, col)

        self.win_curses.bkgd(' ')
        self.win_curses.refresh()

    def _show_lyrics(self):
        print(lyrics.get('Mumford & Sons', 'Sigh no more'))


class SongList(Window):
    def init(self):
        self.win_curses.noutrefresh()

    def draw(self):
        self.win_curses.erase()
        self.win_curses.box()

        self.win_curses.move(1, 1)
        length, max_display = self.clean_position(-2, -2)
        playlist = self.states.playlist
        for i, song in enumerate(playlist.visible_in_window(max_display)):
            if song == self.states.playing and song == playlist.selected:
                col = curses.color_pair(9)
            elif song == playlist.selected:
                col = curses.color_pair(6)
            elif song == self.states.playing:
                col = curses.color_pair(4)
            else:
                col = curses.color_pair(5)

            if song == self.states.playing or song == playlist.selected:
                self.win_curses.hline(i + 1, 1, ' ', length, col)

            self.win_curses.addstr(i + 1, 1, song.format(length), col)

        self.win_curses.refresh()

    def move_cursor(self, y, x=0):
        # later we could also check for other lists here.
        self.states.playlist.move_selected(y)
        self.draw()
