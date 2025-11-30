"""
Structured Logging Configuration
Implements JSON-formatted logging with rotation and transaction ID tracking
"""

import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from src.config import SystemConfig


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter for structured JSON logs
    Ensures all logs include transaction ID and are machine-parseable
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON with standard fields
        """
        # Base log data
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add transaction ID if present
        transaction_id = getattr(record, "transaction_id", None)
        if transaction_id:
            log_data["transaction_id"] = transaction_id
        else:
            log_data["transaction_id"] = "N/A"

        # Add any extra fields passed via 'extra' parameter
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str)


class TourGuideLogger:
    """
    Centralized logger for the Tour Guide system
    Provides convenience methods for logging with transaction context
    """

    def __init__(self, config: SystemConfig):
        self.config = config
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """
        Configure logging system with rotation
        """
        logger = logging.getLogger("tour_guide")
        logger.setLevel(getattr(logging, self.config.log_level.upper()))

        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()

        # Create log directory if needed
        log_path = Path(self.config.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Rotating file handler
        handler = logging.handlers.RotatingFileHandler(
            filename=self.config.log_file_path,
            maxBytes=self.config.log_max_size_mb * 1024 * 1024,
            backupCount=self.config.log_backup_count,
            encoding='utf-8'
        )

        # Set structured formatter
        formatter = StructuredFormatter()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent propagation to root logger (avoid console output)
        logger.propagate = False

        return logger

    def _log(
        self,
        level: int,
        message: str,
        transaction_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Internal logging method with transaction ID support
        """
        extra = {"extra_fields": kwargs}
        if transaction_id:
            extra["transaction_id"] = transaction_id

        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, transaction_id: Optional[str] = None, **kwargs) -> None:
        """Log debug message"""
        self._log(logging.DEBUG, message, transaction_id, **kwargs)

    def info(self, message: str, transaction_id: Optional[str] = None, **kwargs) -> None:
        """Log info message"""
        self._log(logging.INFO, message, transaction_id, **kwargs)

    def warning(self, message: str, transaction_id: Optional[str] = None, **kwargs) -> None:
        """Log warning message"""
        self._log(logging.WARNING, message, transaction_id, **kwargs)

    def error(self, message: str, transaction_id: Optional[str] = None, exc_info: bool = False, **kwargs) -> None:
        """Log error message"""
        if exc_info:
            self.logger.error(
                message,
                extra={"transaction_id": transaction_id or "N/A", "extra_fields": kwargs},
                exc_info=True
            )
        else:
            self._log(logging.ERROR, message, transaction_id, **kwargs)

    def critical(self, message: str, transaction_id: Optional[str] = None, exc_info: bool = False, **kwargs) -> None:
        """Log critical message"""
        if exc_info:
            self.logger.critical(
                message,
                extra={"transaction_id": transaction_id or "N/A", "extra_fields": kwargs},
                exc_info=True
            )
        else:
            self._log(logging.CRITICAL, message, transaction_id, **kwargs)

    def log_stage_entry(
        self,
        stage_name: str,
        transaction_id: str,
        **kwargs
    ) -> None:
        """
        Log entry into a pipeline stage
        Standard method for module transitions
        """
        self.info(
            f"Entering stage: {stage_name}",
            transaction_id=transaction_id,
            stage=stage_name,
            **kwargs
        )

    def log_stage_exit(
        self,
        stage_name: str,
        transaction_id: str,
        duration_ms: Optional[int] = None,
        **kwargs
    ) -> None:
        """
        Log exit from a pipeline stage
        Includes duration if provided
        """
        extra_fields = {"stage": stage_name, **kwargs}
        if duration_ms is not None:
            extra_fields["duration_ms"] = duration_ms

        self.info(
            f"Exiting stage: {stage_name}",
            transaction_id=transaction_id,
            **extra_fields
        )

    def log_agent_start(
        self,
        agent_name: str,
        transaction_id: str,
        waypoint_id: int,
        **kwargs
    ) -> None:
        """Log agent execution start"""
        self.debug(
            f"{agent_name} agent started",
            transaction_id=transaction_id,
            agent_name=agent_name,
            waypoint_id=waypoint_id,
            **kwargs
        )

    def log_agent_completion(
        self,
        agent_name: str,
        transaction_id: str,
        waypoint_id: int,
        status: str,
        execution_time_ms: int,
        **kwargs
    ) -> None:
        """Log agent execution completion"""
        self.info(
            f"{agent_name} agent completed",
            transaction_id=transaction_id,
            agent_name=agent_name,
            waypoint_id=waypoint_id,
            status=status,
            execution_time_ms=execution_time_ms,
            **kwargs
        )

    def log_agent_error(
        self,
        agent_name: str,
        transaction_id: str,
        waypoint_id: int,
        error_message: str,
        **kwargs
    ) -> None:
        """Log agent error"""
        self.error(
            f"{agent_name} agent error",
            transaction_id=transaction_id,
            agent_name=agent_name,
            waypoint_id=waypoint_id,
            error_message=error_message,
            **kwargs
        )

    def log_judge_decision(
        self,
        transaction_id: str,
        waypoint_id: int,
        winner: str,
        confidence: float,
        reasoning: str,
        **kwargs
    ) -> None:
        """Log judge decision"""
        self.info(
            "Judge decision made",
            transaction_id=transaction_id,
            waypoint_id=waypoint_id,
            winner=winner,
            confidence=confidence,
            reasoning=reasoning,
            **kwargs
        )

    def log_waypoint_enrichment(
        self,
        transaction_id: str,
        waypoint_id: int,
        location_name: str,
        selected_type: str,
        processing_time_ms: int,
        agent_success_count: int,
        **kwargs
    ) -> None:
        """Log waypoint enrichment completion"""
        self.info(
            "Waypoint enrichment completed",
            transaction_id=transaction_id,
            waypoint_id=waypoint_id,
            location_name=location_name,
            selected_type=selected_type,
            processing_time_ms=processing_time_ms,
            agent_success_count=agent_success_count,
            **kwargs
        )


# Global logger instance
_logger: Optional[TourGuideLogger] = None


def get_logger() -> TourGuideLogger:
    """
    Get global logger instance
    Initializes on first call
    """
    global _logger
    if _logger is None:
        from src.config import get_config
        config = get_config()
        _logger = TourGuideLogger(config)

    return _logger


def setup_logging(config: SystemConfig) -> TourGuideLogger:
    """
    Setup logging system with provided configuration
    Returns configured logger
    """
    global _logger
    _logger = TourGuideLogger(config)
    return _logger
