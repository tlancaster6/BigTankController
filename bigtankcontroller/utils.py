import logging
from logging import FileHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path
from functools import wraps

def configure_logger(logger: logging.Logger, log_dir):
    """
    configure a logger

    This function should be called towards the beginning of any entry-point/top-level script to configure the parent
    logger, after calling "logger=logging.get_logger()" to get the root logger instance. Module scripts
    should still call "logger=logging.get_logger(__name__)", but not this function, so that the log settings propagate
    properly.

    :param logger: logger instance to configure.
    :param log_dir: directory in which to save log files. Can be a string or pathlib.Path object
    :return: configured logger instance
    """
    # if the logger already has handlers, return it without duplicating configuration
    if logger.handlers:
        logger.warning('a logger that already has handlers should not be passed to configure_logger.')
        return logger

    logger.setLevel(logging.DEBUG)

    # if the logger has not been initiated, set it up
    formatter = logging.Formatter(fmt='%(asctime)s %(name)-16s %(levelname)-8s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    log_dir = Path(log_dir)
    log_dir.mkdir(exist_ok=True, parents=True)
    debug_log_path = log_dir / 'debug.log'
    info_log_path = log_dir / 'info.log'

    fh_debug = RotatingFileHandler(str(debug_log_path), maxBytes=500000, backupCount=2)
    fh_debug.setLevel(logging.DEBUG)
    fh_debug.setFormatter(formatter)
    fh_info = FileHandler(str(info_log_path))
    fh_info.setLevel(logging.INFO)
    fh_info.setFormatter(formatter)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)

    logger.addHandler(fh_info)
    logger.addHandler(fh_debug)
    logger.addHandler(ch)


def generate_logging_decorator(logger: logging.Logger):
    """
    Decorator function to log debug information for a function.

    Args:
        logger (logging.Logger): The logger object to write debug information to.

    Returns:
        The decorated function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_message = f"Calling function: {func.__name__}"
            if args:
                log_message += f" with args: {args}"
            if kwargs:
                log_message += f" and kwargs: {kwargs}"
            logger.debug(log_message)

            try:
                result = func(*args, **kwargs)
                logger.debug(f"Function {func.__name__} returned: {result}")
                return result
            except Exception as e:
                 logger.exception(f"Exception in {func.__name__}: {e}")
                 raise
        return wrapper
    return decorator
