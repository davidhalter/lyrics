"""
Lyrics player

Usage:
  lyrics [<path>] [--debug]
  lyrics -h | --help
  lyrics --version
  lyrics --add <path>

Options:
  -h --help     Show this screen.
  --add         Add something to the music library.
  --version     Show version.
  --debug       Write a debug log.
"""

import sys
import os

import docopt

d = os.path.dirname
sys.path.insert(0, d(d(d(d(os.path.abspath(__file__))))))

import lyrics
from states import state
import playlist
from lyrics import debug
from app import main_app


def start():
    arguments = docopt.docopt(__doc__, version=lyrics.__version__)
    debug.use_debugging = arguments['--debug']
    debug.debug('started with', arguments)

    state.playlist = playlist.Playlist.from_path(arguments['<path>'])
    main_app.start()

if __name__ == '__main__':
    start()
