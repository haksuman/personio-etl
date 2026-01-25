import logging
import sys
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str = "personio_etl", level: str = "INFO") -> logging.Logger:
    """Sets up a logger with console and file handlers."""
    logger = logging.getLogger(name)
    
    # If logger already has handlers, don't add them again
    if logger.handlers:
        return logger
        
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional, but good for persistence in docker volume)
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, "app.log"),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

# Create a default logger instance
logger = setup_logger()
