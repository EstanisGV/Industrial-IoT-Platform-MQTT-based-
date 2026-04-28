import logging
import sys
from pythonjsonlogger import jsonlogger


def setup_logger(settings: dict) -> logging.Logger:
    logger = logging.getLogger("plc-collector")
    logger.setLevel(settings["env"]["LOG_LEVEL"].upper())

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s %(event)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
