import logging
import logging.config

from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "log"

LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    
    "formatters": {
        "default": {
            "format": "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        },
    },
    
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_DIR / "app.log",
            "formatter": "default",  
        },
    },
    
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
}

def logger_config():
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / f"app_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.log"
    LOGGER_CONFIG["handlers"]["file"]["filename"] = log_file

    logging.config.dictConfig(LOGGER_CONFIG)
    return log_file
