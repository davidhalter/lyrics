"""Some settings for the lyrics library"""

use_database = True
""" use a local database to cache """

import os
config_directory = os.path.join(os.getenv('HOME'), '.lyrics')
"""the config directory"""

try:
    os.makedirs(config_directory)
except OSError:
    pass  # directory already exists

database_path = os.path.join(config_directory, 'lyrics.db')
"""the path to the database"""

save_not_found_lyrics = True
"""Also save the lyrics that have not been found, so that they don't have to be
queried again"""
