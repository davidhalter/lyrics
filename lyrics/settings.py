""" Some settings for the lyrics library """

""" use a local database to cache """
use_database = True

import os
config_directory = os.path.join(os.getenv('HOME'), '.lyrics')

try:
    os.makedirs(config_directory)
except OSError:
    pass  # directory already exists

database_path = os.path.join(config_directory, 'lyrics.db')
