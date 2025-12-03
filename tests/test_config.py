"""
Unit tests for src/config.py
Tests configuration management and validation
"""

import pytest
import os
from src.config import SystemConfig, get_config, set_config


@pytest.mark.unit
class TestSystemConfig:
    """Test SystemConfig data structure and validation"""

    def test_config_defaults(self):
        """Test that default configuration values are set correctly"""
        config = SystemConfig()
        assert config.mock_mode == True
        assert config.agent_timeout_ms == 5000
        assert config.max_concurrent_waypoints == 5
        assert config.log_level == "INFO"

    def test_config_from_env(self, monkeypatch):
        """Test loading configuration from environment variables"""
        monkeypatch.setenv("MOCK_MODE", "false")
        monkeypatch.setenv("AGENT_TIMEOUT_MS", "10000")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("GOOGLE_MAPS_API_KEY", "test_key")
        monkeypatch.setenv("YOUTUBE_API_KEY", "test_youtube")

        config = SystemConfig.from_env()
        assert config.mock_mode == False
        assert config.agent_timeout_ms == 10000
        assert config.log_level == "DEBUG"
        assert config.google_maps_api_key == "test_key"

    def test_config_validation_success(self):
        """Test successful configuration validation"""
        config = SystemConfig(
            mock_mode=False,
            google_maps_api_key="test_key",
            youtube_api_key="test_youtube_key",
            agent_timeout_ms=5000,
            judge_timeout_ms=3000
        )
        errors = config.validate()
        assert len(errors) == 0

    def test_config_validation_missing_api_keys(self):
        """Test validation fails when API keys missing in production mode"""
        config = SystemConfig(
            mock_mode=False,
            google_maps_api_key="",
            youtube_api_key=""
        )
        errors = config.validate()
        assert len(errors) > 0
        assert any("GOOGLE_MAPS_API_KEY" in error for error in errors)

    def test_config_validation_invalid_timeouts(self):
        """Test validation fails for invalid timeout values"""
        config = SystemConfig(
            agent_timeout_ms=-100,
            judge_timeout_ms=0
        )
        errors = config.validate()
        assert len(errors) >= 2
        assert any("agent_timeout_ms" in error for error in errors)

    def test_config_validation_invalid_log_level(self):
        """Test validation fails for invalid log level"""
        config = SystemConfig(log_level="INVALID")
        errors = config.validate()
        assert len(errors) > 0
        assert any("log_level" in error for error in errors)

    def test_config_validation_allows_mock_mode_without_keys(self):
        """Test that mock mode doesn't require API keys"""
        config = SystemConfig(
            mock_mode=True,
            google_maps_api_key="",
            youtube_api_key=""
        )
        errors = config.validate()
        # Should not have API key errors in mock mode
        assert not any("API_KEY" in error for error in errors)

    def test_ensure_log_directory(self, tmp_path):
        """Test log directory creation"""
        log_file = tmp_path / "logs" / "test.log"
        config = SystemConfig(log_file_path=str(log_file))
        config.ensure_log_directory()
        assert log_file.parent.exists()


@pytest.mark.unit
class TestConfigSingleton:
    """Test global configuration management"""

    def test_get_config(self, mock_config):
        """Test getting global config instance"""
        config = get_config()
        assert config is not None
        assert isinstance(config, SystemConfig)

    def test_set_config(self):
        """Test setting global config instance"""
        custom_config = SystemConfig(
            mock_mode=False,
            agent_timeout_ms=10000
        )
        set_config(custom_config)
        config = get_config()
        assert config.agent_timeout_ms == 10000

    def test_config_singleton_behavior(self, mock_config):
        """Test that get_config returns same instance"""
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2
