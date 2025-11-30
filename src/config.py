"""
System Configuration
Centralized configuration management for the Tour Guide system
"""

from dataclasses import dataclass
from typing import Optional
import os
from pathlib import Path


@dataclass
class SystemConfig:
    """
    Global system configuration
    Loads from environment variables with sensible defaults
    """

    # API Keys
    google_maps_api_key: str = ""
    youtube_api_key: str = ""
    spotify_client_id: str = ""
    spotify_client_secret: str = ""

    # Timeouts (milliseconds)
    agent_timeout_ms: int = 5000
    judge_timeout_ms: int = 3000
    route_retrieval_timeout_ms: int = 10000

    # Concurrency
    max_concurrent_waypoints: int = 5
    max_agent_threads: int = 50

    # Logging
    log_level: str = "INFO"
    log_file_path: str = "./logs/tour-guide.log"
    log_max_size_mb: int = 100
    log_backup_count: int = 5

    # Performance
    enable_caching: bool = True
    cache_ttl_seconds: int = 3600

    # Development
    mock_mode: bool = True  # Use mock agents/APIs during development

    @classmethod
    def from_env(cls) -> "SystemConfig":
        """
        Load configuration from environment variables
        Falls back to defaults if not set
        """
        return cls(
            # API Keys
            google_maps_api_key=os.getenv("GOOGLE_MAPS_API_KEY", ""),
            youtube_api_key=os.getenv("YOUTUBE_API_KEY", ""),
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID", ""),
            spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET", ""),

            # Timeouts
            agent_timeout_ms=int(os.getenv("AGENT_TIMEOUT_MS", "5000")),
            judge_timeout_ms=int(os.getenv("JUDGE_TIMEOUT_MS", "3000")),
            route_retrieval_timeout_ms=int(os.getenv("ROUTE_RETRIEVAL_TIMEOUT_MS", "10000")),

            # Concurrency
            max_concurrent_waypoints=int(os.getenv("MAX_CONCURRENT_WAYPOINTS", "5")),
            max_agent_threads=int(os.getenv("MAX_AGENT_THREADS", "50")),

            # Logging
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file_path=os.getenv("LOG_FILE_PATH", "./logs/tour-guide.log"),
            log_max_size_mb=int(os.getenv("LOG_MAX_SIZE_MB", "100")),
            log_backup_count=int(os.getenv("LOG_BACKUP_COUNT", "5")),

            # Performance
            enable_caching=os.getenv("ENABLE_CACHING", "true").lower() == "true",
            cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "3600")),

            # Development
            mock_mode=os.getenv("MOCK_MODE", "true").lower() == "true"
        )

    def ensure_log_directory(self) -> None:
        """Create log directory if it doesn't exist"""
        log_path = Path(self.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    def validate(self) -> list[str]:
        """
        Validate configuration
        Returns list of validation errors (empty if valid)
        """
        errors = []

        # Check API keys in non-mock mode
        if not self.mock_mode:
            if not self.google_maps_api_key:
                errors.append("GOOGLE_MAPS_API_KEY is required in non-mock mode")
            if not self.youtube_api_key:
                errors.append("YOUTUBE_API_KEY is required in non-mock mode")
            if not self.spotify_client_id or not self.spotify_client_secret:
                errors.append("SPOTIFY credentials are required in non-mock mode")

        # Check timeout values
        if self.agent_timeout_ms <= 0:
            errors.append("agent_timeout_ms must be positive")
        if self.judge_timeout_ms <= 0:
            errors.append("judge_timeout_ms must be positive")

        # Check concurrency values
        if self.max_concurrent_waypoints <= 0:
            errors.append("max_concurrent_waypoints must be positive")
        if self.max_agent_threads <= 0:
            errors.append("max_agent_threads must be positive")

        # Check log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level.upper() not in valid_levels:
            errors.append(f"log_level must be one of {valid_levels}")

        return errors


# Global configuration instance
_config: Optional[SystemConfig] = None


def get_config() -> SystemConfig:
    """
    Get global configuration instance
    Loads from environment on first call
    """
    global _config
    if _config is None:
        _config = SystemConfig.from_env()
        _config.ensure_log_directory()

        # Validate configuration
        errors = _config.validate()
        if errors and not _config.mock_mode:
            # Only raise errors in production mode
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

    return _config


def set_config(config: SystemConfig) -> None:
    """
    Set global configuration instance
    Useful for testing
    """
    global _config
    _config = config
