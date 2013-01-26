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
            self._connection.row_factory = sqlite3.Row
            self._cursor = self._connection.cursor()
            # Create table
            self._cursor.execute(self._create_table)
        return self._cursor

    def save(self, *args):
        self.cursor.execute(self._insert, args)
        self._connection.commit()

    def load(self, *args):
        self.cursor.execute(self._select, args)
        row = self.cursor.fetchone()
        return row[0] if row is not None else None


class ID3Cache(object):
    _create_table = \
    """
    CREATE TABLE IF NOT EXISTS id3_cache(
        path text primary key,
        artist text not null,
        song text not null,
        album text not null,
        genre text not null,
        year text not null,
        track text not null
    )
    """
    _select = "SELECT * FROM id3_cache WHERE path=?"
    _insert = """INSERT INTO id3_cache VALUES (
                    :path, :artist, :song, :album, :genre, :year, :track)"""
    def __init__(self):
        self._cursor = None

    @property
    def cursor(self):
        if not self._cursor:
            self._cursor = _LyricsDb.cursor
            self._connection = _LyricsDb._connection
            # Create table
            self._cursor.execute(self._create_table)
        return self._cursor

    def save(self, dct):
        self.cursor.execute(self._insert, dct)
        self._connection.commit()

    def load(self, path):
        self.cursor.execute(self._select, (path,))
        row = self.cursor.fetchone()
        return None if row is None else dict(zip(row.keys(), row))


_LyricsDb = _LyricsDb()
ID3Cache = ID3Cache()
