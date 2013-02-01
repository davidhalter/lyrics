import curses

_BACKGROUND = -1

def init():
    curses.use_default_colors()
    global DEFAULT, BLUE, GREEN, BG_MAGENTA, BG_GREEN

    DEFAULT = curses.color_pair(0)

    curses.init_pair(1, curses.COLOR_BLUE, _BACKGROUND)
    BLUE = curses.color_pair(1)

    curses.init_pair(2, curses.COLOR_GREEN, _BACKGROUND)
    GREEN = curses.color_pair(2)

    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_MAGENTA)
    BG_MAGENTA = curses.color_pair(3)

    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_GREEN)
    BG_GREEN = curses.color_pair(4)
