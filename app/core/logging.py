"""
Structured logging module with JSON and text format support.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from app.core.config import get_settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Parameters:
            record (logging.LogRecord): Log record to format
            
        Returns:
            str: JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "route"):
            log_data["route"] = record.route

        if hasattr(record, "method"):
            log_data["method"] = record.method

        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code

        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Custom text formatter for human-readable logging."""

    def __init__(self):
        """Initialize text formatter with custom format."""
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def setup_logging() -> logging.Logger:
    """
    Setup application logging based on configuration.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    settings = get_settings()
    
    logger = logging.getLogger("llm_service")
    logger.setLevel(getattr(logging, settings.logging.level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, settings.logging.level.upper()))
    
    # Set formatter based on configuration
    if settings.logging.format == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = "llm_service") -> logging.Logger:
    """
    Get logger instance by name.
    
    Parameters:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


# Initialize default logger
logger = setup_logging()
