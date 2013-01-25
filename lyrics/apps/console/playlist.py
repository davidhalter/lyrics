import os
import random

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

    def format(self, max_len, album=False):
        """produce something liket this: 'sigh no.. - mumford a..'"""
        if self.artist is None:
            if len(self.file_name) > max_len:
                return self.file_name[:max_len - 2]  + '..'
            else:
                return self.file_name

        song = str(self.song)
        new_len = int(0.5 * max_len)
        if len(song) > new_len:
            song = song[:new_len - 2] + '..'

        max_a_len = max_len - len(song) - 3
        artist = str(self.artist)
        if len(artist) > max_a_len:
            artist = artist[:max_a_len - 2] + '..'

        result = "%s - %s" % (song, artist)
        if album and len(result) < max_len - 5 and self.album:
            result += ' [%s]' % str(self.album[:max_len - len(result) - 3])
        return result

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
        return self._information.get('TIT2', self.path)

    @property
    def album(self):
        return str(self._information.get('TALB', None))

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

    def next(self, song):
        if song is None:
            return self.selected
        i = self.songs.index(song)
        try:
            return self.songs[i + 1]
        except IndexError:
            return None

    def previous(self, song):
        if song is None:
            return self.selected
        i = self.songs.index(song)
        if i == 0:
            return None
        else:
            return self.songs[i - 1]


    def random(self, song=None):
        if len(self.songs) == 1:
            return self.songs[0]
        elif len(self.songs) == 0:
            return None
        while True:
            s = random.randint(0, len(self.songs) - 1)
            if s != song:
                break
        return self.songs[s]

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
        #debug.debug('song paths', paths)
        return cls([Song(os.path.join(path, p)) for p in paths])

    @classmethod
    def from_library(cls):
        # TODO implement
        return cls([])
