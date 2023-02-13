import logging

LOGGING_FORMAT = "[%(asctime)s-%(levelname).4s]: %(message)s"
LOG_LEVEL_MAP = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}
