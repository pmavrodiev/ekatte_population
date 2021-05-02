import logging as _logging
import os
import errno
import types


def log_newline(self, how_many_lines: int = 1):
    """Adds a convenience method to output a new line into a file handler.
       If the logging object doesn't have a file handler defined,
       it won't do anything.
    Args:
        how_many_lines (int, optional): 
            How many new lines to output
    
    Usage: 
       logger.log_newline()
    """
    file_handler = None
    if self.handlers:
        file_handler = self.handlers[0]

    # Switch formatter, output a blank line
    file_handler.setFormatter(self.blank_formatter)
    for i in range(how_many_lines):
        self.info('')

    # Switch back
    file_handler.setFormatter(self.default_formatter)


def setup_custom_logger(
    name: str = 'root',
    logging_level: int = 20,  # 20 = logging.INFO
    flog: str = None,
    log_format: str = ('%(levelname)s:'
                       '[%(module)s](%(funcName)s):\t%(message)s')):
    """Sets up a logging object with custom log format and logging level

    Args:
        name (str): Name of the logger. If not provided defaults to the
                    standard 'root' logger from logging
        
        logging_level (int): The desired logging level. Defaults to logging.INFO
        
        flog (str, optional): An optional path to a file where to output the
        logs. The path must be resolvable by os.path.exists. To be safe
        prefer absolute paths.
        If not provided outputs to the console. Defaults to None.
        
        log_format (str, optional): The desired logging format.
                Must be compatible with the Python logging module.

    Returns:
        logger: A custom logging object ready to be used
    """

    # initialize the default logging subsystem
    _logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S')

    # set-up with custom settings
    logger = _logging.getLogger(name)
    logger.setLevel(logging_level)

    formatter = _logging.Formatter(fmt=log_format)
    logger.default_formatter = formatter
    logger.blank_formatter = _logging.Formatter(fmt="")
    logger.newline = types.MethodType(log_newline, logger)

    if flog is not None:
        # set-up logging to a file
        if not os.path.exists(os.path.dirname(flog)):
            try:
                os.makedirs(os.path.dirname(flog))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # create a file handler
        fhandler = _logging.FileHandler(flog)
        fhandler.setFormatter(formatter)
        fhandler.setLevel(logging_level)
        logger.addHandler(fhandler)

    return logger


def add_file_handler_to_logger(
    logger,
    flogging_level=_logging.DEBUG,
    flog=None,
    log_format: str = ('%(asctime)s - %(levelname)s - '
                       '[%(module)s](%(funcName)s)\t%(message)s')):
    """Adds more files to a logging object.

    Args:
        logger ([type]): [description]
        flogging_level ([type], optional): [description]. Defaults to logging.DEBUG.
        flog ([type], optional): [description]. Defaults to None.
        log_format (str, optional): [description]. Defaults to '%(asctime)s - %(levelname)s - [%(module)s](%(funcName)s)\t%(message)s'.

    Raises:
        TypeError: [description]

    Returns:
        [type]: [description]
    """

    if flog is None:
        raise TypeError("setup_custom_logger::Argument flog cannot be None")

    if not os.path.exists(os.path.dirname(flog)):
        try:
            os.makedirs(os.path.dirname(flog))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    formatter = _logging.Formatter(fmt=log_format)
    fhandler = _logging.FileHandler(flog)
    fhandler.setFormatter(formatter)
    fhandler.setLevel(flogging_level)

    logger.addHandler(fhandler)
    return logger


if __name__ == '__main__':
    l = setup_custom_logger(name='ubsfair', logging_level=logging.ERROR)
    l.warning('warning: hello world')
    l.info('info: hello world')
    l.debug('debug: hello world')
    l.error('error: Hello world')
