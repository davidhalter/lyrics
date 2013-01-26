import os
import mutagen.mp3
import database

class Song(object):
    def __init__(self, path, use_cache=False):
        self.path = path
        self.use_cache = use_cache
        self.__information = None
        self.broken = False

    @property
    def file_name(self):
        return os.path.basename(self.path)

    @property
    def file_name_no_extension(self):
        return self.file_name.rsplit(os.extsep, 1)

    @property
    def _information(self):
        if self.__information is None:
            if self.use_cache:
                self.__information = database.ID3Cache.load(self.path)

            if self.__information is None:
                try:
                    self.__information = mutagen.File(self.path)
                except mutagen.mp3.HeaderNotFoundError:
                    self.__information = {}
                    self.broken = True
                else:
                    if self.use_cache:
                        database.ID3Cache.save(self.export())
        return self.__information

    @property
    def artist(self):
        return str(self._information.get('TPE1', ''))

    @property
    def song(self):
        return str(self._information.get('TIT2', self.path))

    @property
    def album(self):
        return str(self._information.get('TALB', ''))

    @property
    def year(self):
        return str(self._information.get('TDRC', ''))

    @property
    def track(self):
        return str(self._information.get('TRCK', ''))

    @property
    def genre(self):
        return str(self._information.get('TCON', ''))

    def export(self):
        """ export all useful id3 values """
        return dict(song=self.song, artist=self.artist, album=self.album,
                    year=self.year, track=self.track, genre=self.genre,
                    path=self.path)
