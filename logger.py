# logger.py

from __future__ import annotations
from logging.handlers import RotatingFileHandler
from pathlib import Path
from platformdirs import user_log_dir
import logging

APP_NAME = "ExpenseTracker"
LOG_FILENAME = "tracker.log"

def get_log_path() -> Path:
    """Get the Path to the main file of the program

    Returns:
        Path: A path with the log file name added
    """
    base = Path(user_log_dir(APP_NAME))
    base.mkdir(parents=True, exist_ok=True)
    return base / LOG_FILENAME

def logging_cfg(debug: bool = False) -> logging.Logger:
    """Configures a rotational logger in the right file path.

    Args:
        debug (bool, optional): debug instruction.

    Returns:
        logging.Logger: A rotational File Logger.
    """
    # Establishing the file path
    log_path = get_log_path() 
    
    logger = logging.getLogger("expense_tracker")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    # Preventing duplication of logging
    logger.propagate = False 
    
    # Cleaning the old handlers
    if logger.handlers:
        logger.handlers.clear()
        
    # Format 
    format_builder = logging.Formatter(fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                                       datefmt="%Y-%m-%d %H:%M:%S",)
    
    # Rotation (by size)
    file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(format_builder)
    file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.addHandler(file_handler)
    
    # Handler console (Debug)
    if debug:
        console = logging.StreamHandler()
        console.setFormatter(format_builder)
        console.setLevel(logging.DEBUG)
        logger.addHandler(console)
    
    logger.debug("LOGGER CONFIGURED. path=%s debug=%s", log_path, debug)
    return logger

