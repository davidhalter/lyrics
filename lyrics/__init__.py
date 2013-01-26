""" lyrics -- Lyrics fetcher & console music player. """

version_info = (0, 0, 1)

__version__ = version = '.'.join(map(str, version_info))
__project__ = __name__
__author__ = "David Halter"
__license__ = "GPL 3"


import database
import fetcher
import id3

def get(artist, song, album=None):
    """Fetch the lyrics as text."""
    info = artist, song, album or ''
    return database.load(*info) or fetcher.fetch(*info)

def from_file(path, use_id3_cache=False):
    song = id3.Song(path, use_id3_cache)
    if song.artist and song.song:
        args = song.artist, song.song, song.album
    else:
        # If the id3 information isn't enough, just try the filename.
        args = '', song.file_name_no_extension, ''
    return get(*args)
