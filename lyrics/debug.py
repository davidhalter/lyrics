import os
import logging

from lyrics import settings

use_debugging = False
f_name = os.path.join(settings.config_directory, 'lyrics.log')
logging.basicConfig(filename=f_name, level=logging.DEBUG)

def debug(msg, *args):
    if use_debugging:
        logging.debug(_format_msg(msg, *args))

def warning(msg, *args):
    logging.warning(_format_msg(msg, *args))

def _format_msg(msg, *args):
    if args:
        msg = ("%s: " % msg) + ', '.join(str(a) for a in args)
    return msg
