class States(object):
    """State machine of the app"""
    def __init__(self):
        self.playlist = None

        self.split_screen = False
        self.search_list = []
        self.search_index = 0
        self.search_cursor = 0
        self.search = ''
        self.search_mode = False

        self.playing = None
        self.current_window = None

        self.keyboard_repeat = ''
        self.command_list = []

        self.fetched_songs = []

        self._last_command = ''
        self._random = False
        self._show_help = False
        self._lyrics = False
        self._repeat = True
        self._repeat_solo = False

        self.window_head = None
        self.window_song_list = None
        self.window_lyrics = None
        self.window_status_list = None
        self.window_footer = None

    @property
    def last_command(self):
        return self._last_command

    @last_command.setter
    def last_command(self, value):
        self._last_command = value
        if value:
            self.command_list.append((self.last_command, self.keyboard_repeat))

    @property
    def random(self):
        return self._random

    @random.setter
    def random(self, value):
        self._random = value
        if self.playing is None:
            self.random_history = []
            self.random_history_index = -1
        else:
            self.random_history = [self.playing]
            self.random_history_index = 0

    @property
    def repeat(self):
        return self._repeat

    @repeat.setter
    def repeat(self, value):
        self._repeat = value
        if value:
            self._repeat_solo = False

    @property
    def repeat_solo(self):
        return self._repeat_solo

    @repeat_solo.setter
    def repeat_solo(self, value):
        self._repeat_solo = value
        if value:
            self._repeat = False

    @property
    def show_help(self):
        return self._show_help

    @show_help.setter
    def show_help(self, value):
        self._show_help = value
        if value:
            self.split_screen = True
        else:
            self.split_screen = self.lyrics

    @property
    def lyrics(self):
        return self._lyrics

    @lyrics.setter
    def lyrics(self, value):
        self._lyrics = value
        if value:
            self.split_screen = True
        elif not self.show_help:
            self.current_window = state.window_song_list
            self.split_screen = False


state = States()
