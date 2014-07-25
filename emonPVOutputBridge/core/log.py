__author__ = 'vm'
import logging
from core.colorstreamhandler import ColorStreamHandler
import sys


def setupCustomLogger(name) -> logging:
    formatter = logging.Formatter(fmt='%(asctime)s - %(module)s - %(levelname)s: %(message)s')

    handler = ColorStreamHandler(stream=sys.stdout)

    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger