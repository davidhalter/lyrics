import sqlite3

import settings

def load(artist, song, album):
    if settings.use_database:
        return _LyricsDb.load()
    else:
        return None


def save(artist, song, album, lyrics):
    if settings.use_database:
        return _LyricsDb.save()


class _LyricsDb(object):
    _create_table = \
    """
    CREATE TABLE lyrics(
        artist text not null,
        song text not null,
        album text not null,
        lyrics text not null,
        unique(artist, song, album)
    )
    """
    _select = "SELECT lyrics FROM lyrics WHERE artist=? and song=? and album=?"
    _insert = "INSERT INTO lyrics VALUES (?, ?, ?, ?)"
    def __init__(self):
        self.__cursor = None

    @property
    def cursor(self):
        if not self._cursor:
            self._connection = sqlite3.connect(settings.config_directory)
            self._cursor = self._connection.cursor()
            # Create table
            self._cursor.execute(self._create_table)
        return self._cursor

    def save(self, *args):
        self.cursor.execute(self._insert, args)

    def load(self, *args):
        self.cursor.execute(self._select, args)
        return self.cursor.fetchone()[0]

_LyricsDb = _LyricsDb()
