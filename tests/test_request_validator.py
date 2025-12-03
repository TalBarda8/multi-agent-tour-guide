"""
Unit tests for src/modules/request_validator.py
Tests input validation and transaction context creation
"""

import pytest
from src.modules.request_validator import validate_request, ValidationError


@pytest.mark.unit
class TestRequestValidator:
    """Test request validation module"""

    def test_valid_request(self):
        """Test validation of valid request"""
        context = validate_request(
            origin="New York",
            destination="Boston",
            preferences={"content_type": "auto"}
        )
        assert context is not None
        assert context.origin == "New York"
        assert context.destination == "Boston"
        assert context.transaction_id.startswith("TXID-")

    def test_empty_origin(self):
        """Test validation fails for empty origin"""
        with pytest.raises(ValidationError) as exc_info:
            validate_request(
                origin="",
                destination="Boston"
            )
        assert "origin" in str(exc_info.value).lower()

    def test_empty_destination(self):
        """Test validation fails for empty destination"""
        with pytest.raises(ValidationError) as exc_info:
            validate_request(
                origin="New York",
                destination=""
            )
        assert "destination" in str(exc_info.value).lower()

    def test_whitespace_only_origin(self):
        """Test validation fails for whitespace-only origin"""
        with pytest.raises(ValidationError):
            validate_request(
                origin="   ",
                destination="Boston"
            )

    def test_none_origin(self):
        """Test validation fails for None origin"""
        with pytest.raises((ValidationError, TypeError)):
            validate_request(
                origin=None,
                destination="Boston"
            )

    def test_preferences_normalization(self):
        """Test that preferences are properly normalized"""
        context = validate_request(
            origin="New York",
            destination="Boston",
            preferences=None
        )
        assert context.user_preferences == {} or context.user_preferences.get("content_type") is not None

    def test_transaction_id_uniqueness(self):
        """Test that each validation creates unique transaction ID"""
        context1 = validate_request("A", "B")
        context2 = validate_request("A", "B")
        assert context1.transaction_id != context2.transaction_id

    def test_context_initial_stage(self):
        """Test that context is initialized with correct stage"""
        context = validate_request("New York", "Boston")
        assert context.current_stage in ["initialization", "validation"]

    def test_long_location_names(self):
        """Test validation with very long location names"""
        long_origin = "A" * 500
        long_dest = "B" * 500
        context = validate_request(long_origin, long_dest)
        assert context.origin == long_origin
        assert context.destination == long_dest

    def test_special_characters_in_locations(self):
        """Test validation handles special characters"""
        origin = "São Paulo, Brazil"
        destination = "Zürich, Switzerland"
        context = validate_request(origin, destination)
        assert context.origin == origin
        assert context.destination == destination
