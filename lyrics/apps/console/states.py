class States(object):
    """State machine of the app"""
    def __init__(self):
        self.playlist = None

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


state = States()
