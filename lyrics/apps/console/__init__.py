"""
Lyrics player

Usage:
  lyrics
  lyrics <path>
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
import app


def start():
    arguments = docopt.docopt(__doc__, version=lyrics.__version__)
    print arguments
    app.App(arguments['<path>'], debug=bool(arguments['<debug>']))

if __name__ == '__main__':
    start()
