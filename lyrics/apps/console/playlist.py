import os
from os.path import join, abspath, expanduser, expandvars
import random

from lyrics import debug
from lyrics import id3
from lyrics._compatibility import unicode


class Song(object):
    def __init__(self, path):
        self._song = id3.Song(path, use_cache=True)

    def __getattr__(self, name):
        return getattr(self._song, name)

    def format(self, max_len, album=False):
        """produce something liket this: 'sigh no.. - mumford a..'"""
        if not self.artist:
            if len(self.file_name) > max_len:
                return self.file_name[:max_len - 2]  + '..'
            else:
                return self.file_name

        song = unicode(self.song)
        new_len = int(0.5 * max_len)
        if len(song) > new_len:
            song = song[:new_len - 2] + '..'

        max_a_len = max_len - len(song) - 3
        artist = unicode(self.artist)
        if len(artist) > max_a_len:
            artist = artist[:max_a_len - 2] + '..'

        result = "%s - %s" % (song, artist)
        if album and len(result) < max_len - 5 and self.album:
            result += ' [%s]' % unicode(self.album[:max_len - len(result) - 3])
        return result

    def search(self, string):
        return string.lower() in self.album.lower() \
                or string.lower() in self.song.lower() \
                or string.lower() in self.artist.lower()


class Playlist(object):
    def __init__(self, songs, selected=None, parent=None):
        self.parent = parent
        self.songs = songs
        self.sort()
        self.selected = selected or self.songs[0] if self.songs else None

    def __len__(self):
        return len(self.songs)

    def __getitem__(self, key):
        return self.songs[key]

    def sort(self):
        sort_func = lambda song: (not song.artist, song.artist, song.song)
        self.songs = sorted(self.songs, key=sort_func)

    def search(self, string):
        return Playlist([s for s in self.songs if s.search(string)],
                                selected=self.selected, parent=self)

    def _set_index(self):
        try:
            self.index = self.songs.index(self.selected)
        except  ValueError:
            self.index = 0

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
    def from_path(cls, paths, recursive=True):
        if not paths:
            return cls.from_library()

        def is_sound(path):
            return path[-4:] in ('.mp3', '.wav', '.ogg', '.wmv', 'm3u') \
                or path[-5:] == '.flac'

        debug.debug('load from', paths)
        new_paths = []
        for path in paths:
            path = path.decode('UTF-8')
            path = abspath(expandvars(expanduser(path)))
            for root, dirs, files in os.walk(path):
                for name in files:
                    p = join(root, name)
                    if is_sound(p):
                        new_paths.append(p)
                if recursive is False:
                    break
        #debug.debug('song paths', paths)
        return cls([Song(p) for p in new_paths])

    @classmethod
    def from_library(cls):
        # TODO implement
        return cls([])
