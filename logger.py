"""
Enhanced logging setup for OracleXBT
"""

import logging
import logging.handlers
from pathlib import Path
from config_loader import config

def setup_logging():
    """Configure logging for the application"""
    
    # Create logs directory if it doesn't exist
    log_config = config.logging_config
    log_file = log_config.get('file', 'logs/oraclexbt.log')
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    # Get log level
    level_name = log_config.get('level', 'INFO')
    level = getattr(logging, level_name, logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=log_config.get('max_bytes', 10485760),  # 10MB
        backupCount=log_config.get('backup_count', 5)
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create application logger
    logger = logging.getLogger('oraclexbt')
    logger.info("Logging initialized")
    
    return logger

# Global logger
logger = setup_logging()
