""" lyrics -- Lyrics fetcher & console music player. """

version_info = (0, 0, 1)

__version__ = version = '.'.join(map(str, version_info))
__project__ = __name__
__author__ = "David Halter"
__license__ = "GPL 3"


import database
import fetcher

def get(artist, song, album=None):
    info = artist, song, album
    return database.load(*info) or fetcher.fetch(*info)
