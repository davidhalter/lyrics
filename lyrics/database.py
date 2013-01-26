import sqlite3
import threading

import settings
import debug

def load(artist, song, album):
    if settings.use_database:
        return _LyricsDb.load(artist, song, album)
    else:
        return None


def save(artist, song, album, lyrics):
    if settings.use_database:
        return _LyricsDb.save(artist, song, album, lyrics)


def _get_db_cursor():
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    # Create table
    return connection, cursor


_db_lock = threading.Lock()


def _sqlite_threadsafe(func):
    def wrapper(*args, **kwargs):
        _db_lock.acquire()
        result = func(*args, **kwargs)
        _db_lock.release()
        return result
    return wrapper


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

    def get_cursor(self):
        """create new connections, sqlite cannot handle multi threading"""
        connection, cursor = _get_db_cursor()
        cursor.execute(self._create_table)
        return connection, cursor

    @_sqlite_threadsafe
    def save(self, *args):
        connection, cursor = self.get_cursor()
        cursor.execute(self._insert, args)
        connection.commit()

    @_sqlite_threadsafe
    def load(self, *args):
        connection, cursor = self.get_cursor()
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

    def get_cursor(self):
        """create new connections, sqlite cannot handle multi threading"""
        connection, cursor = _get_db_cursor()
        connection, cursor.execute(self._create_table)
        return connection, cursor

    @_sqlite_threadsafe
    def save(self, dct):
        connection, cursor = self.get_cursor()
        debug.debug('save id3 db song', dct)
        cursor.execute(self._insert, dct)
        connection.commit()

    @_sqlite_threadsafe
    def load(self, path):
        connection, cursor = self.get_cursor()
        cursor.execute(self._select, (path,))
        row = cursor.fetchone()
        if row is None:
            return None
        row = dict(zip(row.keys(), row))
        #debug.debug('id3 db song', row)
        return row


_LyricsDb = _LyricsDb()
ID3Cache = ID3Cache()
