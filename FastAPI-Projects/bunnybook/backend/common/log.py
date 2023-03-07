import logging
import sys


__all__ = "logger"

logger = logging.getLogger("bunnybook")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(levelname)s: %(asctime)s (file: %(filename)s, line: %(lineo)d, func: %(funcName)s) - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)