import logging
import os
from datetime import datetime
from typing import Optional

class ServerLogger:
    def __init__(self):
        # Create logs directory if it doesn't exist
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        # Set up file handlers for different log types
        self.setup_loggers()
    
    def setup_loggers(self):
        # Main logger for all server activity
        self.server_logger = self._setup_logger(
            "server",
            f"{self.logs_dir}/server.log",
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        
        # Query logger for tracking all queries
        self.query_logger = self._setup_logger(
            "queries",
            f"{self.logs_dir}/queries.log",
            "%(asctime)s - %(message)s"
        )
        
        # Error logger for tracking errors
        self.error_logger = self._setup_logger(
            "errors",
            f"{self.logs_dir}/errors.log",
            "%(asctime)s - %(levelname)s - %(message)s\n%(pathname)s:%(lineno)d\n"
        )
    
    def _setup_logger(self, name: str, log_file: str, format_str: str) -> logging.Logger:
        """Set up a logger with the specified configuration."""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(console_handler)
        
        return logger
    
    def log_query(self, query: str, user: Optional[str] = None):
        """Log a user query."""
        log_message = f"Query: {query}"
        if user:
            log_message = f"User: {user} - {log_message}"
        self.query_logger.info(log_message)
    
    def log_error(self, error: Exception, context: Optional[str] = None):
        """Log an error with optional context."""
        error_message = f"Error: {str(error)}"
        if context:
            error_message = f"{context} - {error_message}"
        self.error_logger.error(error_message, exc_info=True)
    
    def log_server_activity(self, message: str, level: str = "info"):
        """Log general server activity."""
        log_method = getattr(self.server_logger, level.lower(), self.server_logger.info)
        log_method(message)
    
    def rotate_logs(self):
        """Rotate log files if they get too large."""
        for logger_name in ["server", "queries", "errors"]:
            log_file = f"{self.logs_dir}/{logger_name}.log"
            if os.path.exists(log_file) and os.path.getsize(log_file) > 5 * 1024 * 1024:  # 5MB
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                os.rename(log_file, f"{log_file}.{timestamp}")
                self.setup_loggers()  # Recreate loggers with new files 