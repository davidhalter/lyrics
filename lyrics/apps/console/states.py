class States(object):
    """State machine of the app"""
    def __init__(self):
        self.playlist = None

        self.split_screen = False
        self.playing = None
        self.current_window = None

        self._random = False
        self._show_help = False
        self._show_lyrics = False
        self._repeat = True
        self._repeat_solo = False

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
            self.split_screen = self.show_lyrics

    @property
    def show_lyrics(self):
        return self._show_lyrics

    @show_lyrics.setter
    def show_lyrics(self, value):
        self._show_lyrics = value
        if value:
            self.split_screen = True


state = States()
