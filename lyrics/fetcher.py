import database

def fetch(artist, song, album, lyrics):
    database.save(artist, song, album, lyrics)
    return None
