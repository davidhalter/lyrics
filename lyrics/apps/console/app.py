""" the curses implementation """

import curses

import player
import lyrics

class App(object):
    def __init__(self):
        curses.wrapper(self.setup)

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

        self.stdscr.nodelay(0)
        self.setupAndDrawScreen()

        self.run()

    def draw(self):
        self.maxY, self.maxX = self.stdscr.getmaxyx()

        self.window_head = curses.newwin(1, self.maxX, 0, 0)
        self.window_list = curses.newwin(self.maxY - 2, self.maxX, 1, 0)
        self.footerWin = curses.newwin(1, self.maxX, self.maxY - 1, 0)
        self.initHead()
        self.initBody()
        self.initFooter()

        self.log.setScreen(self.footerWin)

        #self.stdscr.timeout(100)
        self.bodyWin.keypad(1)

        #self.stdscr.noutrefresh()

        curses.doupdate()

    def run(self):
        while True:
            try:
                c = self.bodyWin.getch()
                print c
                ret = self.keypress(c)
                if (ret == -1):
                    return
            except KeyboardInterrupt:
                break

    def _show_lyrics(self):
        print(lyrics.get('Mumford & Sons', 'Sigh no more'))
