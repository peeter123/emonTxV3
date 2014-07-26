__author__ = 'vm'
import logging
import logging.handlers
import sys

from core.colorstreamhandler import ColorStreamHandler


def setupCustomStdoutLogger(name) -> logging:
    # Create colorstream to stdout
    handler = ColorStreamHandler(stream=sys.stdout)
    return createLogger(name, handler)


def setupCustomFileLogger(name, path) -> logging:
    # Create rotating log handler
    handler = logging.handlers.RotatingFileHandler(path, 'a', 5000 * 1024, 1)
    return createLogger(name, handler)


def createLogger(name, handler) -> logging:
    formatter = logging.Formatter('%(asctime)s - %(module)s - %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    # Instantiate the logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger