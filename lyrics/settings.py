import os
config_directory = os.path.join(os.getenv('HOME'), '.lyrics')

try:
    os.makedirs(config_directory)
except OSError:
    pass  # directory already exists
