"""
Lyrics player

Usage:
  lyrcs
  lyrcs -h | --help
  lyrcs --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import sys
import os

import docopt

d = os.path.dirname
sys.path.insert(0, d(d(d(d(os.path.abspath(__file__))))))

import lyrics


if __name__ == '__main__':
    arguments = docopt.docopt(__doc__, version=lyrics.__version__)
    lyrics.get('Mumford & Sons', 'Sigh no more')
