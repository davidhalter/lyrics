""" the curses implementation """

import curses

import lyrics
import playlist
import keys
import debug

class App(object):
    def __init__(self, path):
        self.playlist = playlist.Playlist.from_path(path)
        self.playing = None

    def start(self):
        curses.wrapper(self.setup)  # must be called at the end (loop)

    def setup(self, stdscr):
        self.stdscr = stdscr

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

        self.max_y, self.max_x = self.stdscr.getmaxyx()

        self.stdscr.nodelay(0)
        self.draw_screen()

        self.run()

    def run(self):
        while True:
            try:
                c = self.window_list.getkey()
                keys.execute_event(self, c)
            except KeyboardInterrupt:
                break

    def draw_screen(self):
        self.window_head = self._new_win(0, 0, None, 1)
        self.window_list = self._new_win(0, 1, None, -2)
        self.window_footer = self._new_win(0, -1, None, 1)

        self.init_head()
        self.init_list()
        self.init_footer()

        #self.stdscr.timeout(100)
        self.window_list.keypad(1)

        #self.stdscr.noutrefresh()

        curses.doupdate()

    def clean_position(self, x, y, type='main'):
        if type == 'main':
            max_x, max_y = self.max_x, self.max_y
        elif type == 'list':
            max_x, max_y = self.max_list_x, self.max_list_y

        if x is None:
            x = max_x
        if y is None:
            y = max_y

        if x < 0:
            x = max_x + x
        if y < 0:
            y = max_y + y
        return x, y

    def _new_win(self, x, y, width=None, height=None):
        x, y = self.clean_position(x, y)
        width, height = self.clean_position(width, height)

        debug.debug('new_win', x, y, width, height)
        return curses.newwin(height, width, y, x)

    def init_head(self):
        info = " lyrics "
        self.window_head.addstr(0, 0, info, curses.color_pair(4))
        right_str = "test"
        x, y = self.clean_position(- len(right_str) - 1, 0)
        debug.debug('test', x, y, self.clean_position(None,None))
        self.window_head.addstr(y, x, right_str, curses.color_pair(2))
        self.window_head.bkgd(' ', curses.color_pair(7))
        self.window_head.noutrefresh()

    def init_list(self):
        self.max_list_y, self.max_list_x = self.window_list.getmaxyx()
        self.window_list.noutrefresh()
        self.draw_song_list()

    def draw_song_list(self):
        self.window_list.erase()
        self.window_list.box()

        self.window_list.move(1, 1)
        length, max_display = self.clean_position(-2, -1, 'list')
        for i, song in enumerate(self.playlist.visible_in_window(max_display)):
            if song == self.playing and song == self.playlist.selected:
                col = curses.color_pair(9)
            elif song == self.playlist.selected:
                col = curses.color_pair(6)
            elif song == self.playing:
                col = curses.color_pair(4)
            else:
                col = curses.color_pair(5)

            if song == self.playing or song == self.playlist.selected:
                self.window_list.hline(i + 1, 1, ' ', length, col)

            self.window_list.addstr(i + 1, 1, repr(song), col)

        self.window_list.refresh()

    def move_cursor(self, count, horizontal_count=0):
        # later we could also check for other lists here.
        self.playlist.move_selected(count)
        self.draw_song_list()

    def init_footer(self):
        self.window_footer.bkgd(' ', curses.color_pair(7))
        self.window_footer.noutrefresh()

    def _show_lyrics(self):
        print(lyrics.get('Mumford & Sons', 'Sigh no more'))
