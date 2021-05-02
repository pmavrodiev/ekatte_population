import logging
import inspect

from .custom_logging import setup_custom_logger

# Logging levels.
CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG

# Logging set-up
name = 'houston'

# check if release or not
try:
    from ubsfair.version import release
    if release is True:
        logging_level = INFO
    else:
        logging_level = DEBUG
except ImportError:
    logging_level = Debug

flog = None
log_format = ('%(levelname)s:houston:'
              '[%(module)s](%(funcName)s:%(lineno)d):\t%(message)s')

# Get a custom logger
logger = None


def setup(name=name,
          logging_level=logging_level,
          flog=flog,
          log_format=log_format):
    logger = setup_custom_logger(name=name,
                                 logging_level=logging_level,
                                 flog=flog,
                                 log_format=log_format)
    return logger


logger = setup(name=name,
               logging_level=logging_level,
               flog=flog,
               log_format=log_format)
#


def error(msg):
    """Logs an error message."""
    logger.error(msg, stacklevel=2)


def warning(msg):
    """Logs a warning message."""
    logger.warning(msg, stacklevel=2)


def info(msg):
    """Logs an info message."""
    logger.info(msg, stacklevel=2)


def debug(msg):
    """Logs a debug message."""
    logger.debug(msg, stacklevel=2)
