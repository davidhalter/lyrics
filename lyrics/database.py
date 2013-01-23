import sqlite3

import settings

def load(artist, song, album):
    if settings.use_database:
        return _LyricsDb.load(artist, song, album)
    else:
        return None


def save(artist, song, album, lyrics):
    if settings.use_database:
        return _LyricsDb.save(artist, song, album, lyrics)


class _LyricsDb(object):
    _create_table = \
    """
    CREATE TABLE IF NOT EXISTS lyrics(
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
        self._cursor = None

    @property
    def cursor(self):
        if not self._cursor:
            self._connection = sqlite3.connect(settings.database_path)
            self._cursor = self._connection.cursor()
            # Create table
            self._cursor.execute(self._create_table)
        return self._cursor

    def save(self, *args):
        self.cursor.execute(self._insert, args)

    def load(self, *args):
        self.cursor.execute(self._select, args)
        row = self.cursor.fetchone()
        return row[0] if row is not None else None

_LyricsDb = _LyricsDb()
