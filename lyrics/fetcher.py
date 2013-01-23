import database
import requests


def fetch(artist, song, album):
    lyrics = LyrDb.fetch(artist, song, album)
    if lyrics:
        database.save(artist, song, album, lyrics)
    return lyrics

class LyrDb(object):
    def __init__(self):
        self.url = 'http://webservices.lyrdb.com/'

    def _search(self, artist, song):
        """ lyrdb.com uses probably a mysql fulltext search """
        url = self.url + "lookup.php?q=%s&for=%s&agent=python_lyrics"
        method = 'fullt'  # search method
        query = "%s|%s" % (artist, song)
        request = requests.get(url % (query, method))
        print request
        search = request.text
        print search
        if not (200 <= request.status_code < 300):
            return None
        return search


    def fetch(self, artist, song, album):
        id = self._search(artist, song)
        if not id:
            return None
        result = requests.get(self.url + "getlyr.php?q=%s" % id).read()
        return result

LyrDb = LyrDb()

