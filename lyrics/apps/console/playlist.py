import os

import mutagen


class Song(object):
    def __init__(self, path):
        self.path = path

    def __repr__(self):
        return "%s - %s" % (self.artist, self.song)

    @property
    def _information(self):
        mutagen.File(self.path)

    @property
    def artist(self):
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



class Playlist(object):
    def __init__(self, songs, parent=None):
        self.songs = songs
        print songs
        self.parent = parent or self
        self.lookat = 0

    def sort(self):
        self.songs = sorted(self.songs)

    def search(self, string):
        return Playlist([s for s in self.songs if s.search(string)], self)

    def in_window_songs(self, count):
        return self.songs[self.lookat:self.lookat + count]

    @classmethod
    def from_path(cls, path):
        if path is None:
            return cls.from_library()
        if os.path.isfile(path):
            paths = [path]
        elif os.path.isdir(path):
            paths = [p for p in os.listdir(path) if os.path.isdir(p)]
        else:
            return cls.from_library()
        print paths
        return cls([Song(p) for p in paths])

    @classmethod
    def from_library(cls):
        # TODO implement
        return cls([])
