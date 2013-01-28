import re

import requests
from bs4 import BeautifulSoup

import database
import debug
from _compatibility import unicode


def fetch(artist, song, album):
    lyrics = Wikia.fetch(artist, song, album)
    if lyrics:
        database.save(artist, song, album, lyrics)
    return lyrics


class Wikia(object):
    def __init__(self):
        self.url = "http://lyrics.wikia.com/api.php?artist=%s&song=%s&fmt=json"

    def fetch(self, artist, song, album):
        if not artist or not song:
            return None  # wikia needs both informations
        r = requests.get(self.url % (artist, song))
        if r.status_code != 200:
            return None

        # The api returns a pseudo json object, that contains a url.
        match = re.search("'url':'([^']+)'", r.text)
        if match is None:
            return None

        html_url = match.group(1)
        debug.debug('fetch url', html_url)
        r = requests.get(html_url)
        if r.status_code != 200:
            return None
        match = re.search(r"<div class='lyricbox'>", r.text)
        #with open('/home/david/test.txt', 'w') as f:
        #    f.write(r.text.encode('UTF-8'))
        if match is None:
            debug.debug('src not found in url', html_url)
            return None

        # parse the result
        soup = BeautifulSoup(r.text)
        lyricbox = soup.find('div', "lyricbox")
        if lyricbox is None:
            debug.debug("BeautifulSoup doesn't find content", html_url)
            return None

        lyrics = ''
        for c in lyricbox.contents:
            text = unicode(c).strip()
            if not text.startswith('<'):
                lyrics += text.strip()
            elif text.startswith('<br'):
                lyrics += '\n'
        return lyrics.strip()


Wikia = Wikia()
