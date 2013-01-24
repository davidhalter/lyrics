import os

import mutagen.mp3

import debug


class Song(object):
    def __init__(self, path):
        self.path = path
        self.__information = None
        self.broken = False

    def __repr__(self):
        if self.artist is None:
            return str(self.file_name)
        return "%s - %s" % (self.artist, self.song)

    def format(self, max_len):
        """produce something liket this: 'sigh no.. - mumford a..'"""
        if self.artist is None:
            return self.file_name[:max_len - 2]  + '..'

        song = str(self.song)
        new_len = int(0.5 * max_len)
        if len(song) > new_len:
            song = song[:new_len - 2] + '..'

        max_a_len = max_len - len(song) - 3
        artist = str(self.artist)
        if len(artist) > max_a_len:
            artist = artist[:max_a_len - 2] + '..'

        return "%s - %s" % (song, artist)

    @property
    def file_name(self):
        return os.path.basename(self.path)

    @property
    def _information(self):
        if self.__information is None:
            debug.debug('mutagen before', self.path)
            try:
                self.__information = mutagen.File(self.path)
            except mutagen.mp3.HeaderNotFoundError:
                self.__information = {}
                self.broken = True
        return self.__information

    @property
    def artist(self):
        return self._information.get('TPE1', None)

    @property
    def song(self):
        song = self._information.get('TIT2', self.path)
        return song

    @property
    def album(self):
        return self._information.get('TALB', None)

    def search(self, string):
        return string in self.album or string in self.song \
                    or string in self.artist


class StringList(object):
    def __init__(self, strings, index=0):
        self.strings = strings
        self.index = 0

    def visible_in_window(self, count):
        length = len(self.songs)
        lookat = max(0, self.index - int(count / 2))
        lookat = min(lookat, length - int(count / 2))

        selection = self.songs[lookat:lookat + count]
        return selection

    def move_selected(self, count):
        """count can be negative"""
        self.index += count
        self.index = min(max(self.index, 0), len(self.strings) - 1)


class Playlist(StringList):
    def __init__(self, songs, selected=None, parent=None):
        super(Playlist, self).__init__(songs)
        self.songs = songs
        self.selected = selected or self.songs[0] if self.songs else None
        self.parent = parent or self

    def sort(self):
        self.songs = sorted(self.songs)

    def search(self, string):
        return Playlist([s for s in self.songs if s.search(string)], self)

    def _set_index(self):
        try:
            self.index = self.songs.index(self.selected)
        except  ValueError:
            self.index = 0

    def visible_in_window(self, *args, **kwargs):
        self._set_index()
        return super(Playlist, self).visible_in_window(*args, **kwargs)

    def move_selected(self, *args, **kwargs):
        self._set_index()
        super(Playlist, self).move_selected(*args, **kwargs)
        self.selected = self.songs[self.index]

    @classmethod
    def from_path(cls, path):
        path = os.path.expandvars(os.path.expanduser(path))
        debug.debug('load from', path)
        if path is None:
            return cls.from_library()
        if os.path.isfile(path):
            paths = [path]
        elif os.path.isdir(path):
            paths = [p for p in os.listdir(path) if not os.path.isdir(p)]
        else:
            return cls.from_library()
        debug.debug('song paths', paths)
        return cls([Song(os.path.join(path, p)) for p in paths])

    @classmethod
    def from_library(cls):
        # TODO implement
        return cls([])
