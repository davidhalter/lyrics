import logging

log = logging.Logger('lyrics.log')

def debug(msg, *args):
    log.debug(msg, *args)
