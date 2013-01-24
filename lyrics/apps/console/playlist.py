import os

import mutagen

import debug


class Song(object):
    def __init__(self, path):
        self.path = path
        self.__information = None

    def __repr__(self):
        return "%s - %s" % (self.artist, self.song)

    @property
    def _information(self):
        if self.__information:
            self.__information = mutagen.File(self.path)
        return self.__information

    @property
    def artist(self):
        debug.debug(self._information)
        return 'bar'

    @property
    def song(self):
        return 'foo'

    @property
    def album(self):
        return 'baz'

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
        debug.debug('load from', path, os.path.isdir(path))
        if path is None:
            return cls.from_library()
        if os.path.isfile(path):
            paths = [path]
        elif os.path.isdir(path):
            paths = [p for p in os.listdir(path) if not os.path.isdir(p)]
        else:
            return cls.from_library()
        debug.debug('song paths', paths)
        return cls([Song(p) for p in paths])

    @classmethod
    def from_library(cls):
        # TODO implement
        return cls([])
