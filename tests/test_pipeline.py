"""
Unit tests for src/pipeline.py
Tests end-to-end pipeline execution
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from src.pipeline import execute_pipeline, execute_pipeline_safe, PipelineError
from src.modules import ValidationError, RouteRetrievalError


@pytest.mark.integration
class TestPipeline:
    """Test main pipeline execution"""

    @patch('src.pipeline.Orchestrator')
    @patch('src.pipeline.retrieve_route')
    @patch('src.pipeline.validate_request')
    def test_successful_pipeline_execution(
        self,
        mock_validate,
        mock_retrieve,
        mock_orchestrator_class,
        transaction_context,
        sample_route_data,
        sample_waypoints
    ):
        """Test complete successful pipeline execution"""
        # Setup mocks
        mock_validate.return_value = transaction_context
        mock_retrieve.return_value = sample_route_data

        mock_orchestrator = MagicMock()
        mock_orchestrator.enrich_route.return_value = sample_waypoints
        mock_orchestrator_class.return_value = mock_orchestrator

        # Execute pipeline
        result = execute_pipeline("New York", "Boston")

        # Verify
        assert "route" in result or "transaction_id" in result
        mock_validate.assert_called_once()
        mock_retrieve.assert_called_once()
        mock_orchestrator.enrich_route.assert_called_once()
        mock_orchestrator.shutdown.assert_called_once()

    @patch('src.pipeline.validate_request')
    def test_pipeline_validation_error(self, mock_validate):
        """Test pipeline handles validation errors"""
        mock_validate.side_effect = ValidationError("Invalid origin")

        with pytest.raises(ValidationError):
            execute_pipeline("", "Boston")

    @patch('src.pipeline.retrieve_route')
    @patch('src.pipeline.validate_request')
    def test_pipeline_route_retrieval_error(
        self,
        mock_validate,
        mock_retrieve,
        transaction_context
    ):
        """Test pipeline handles route retrieval errors"""
        mock_validate.return_value = transaction_context
        mock_retrieve.side_effect = RouteRetrievalError("Route not found")

        with pytest.raises(RouteRetrievalError):
            execute_pipeline("Invalid", "Location")

    def test_safe_pipeline_returns_error_dict_on_validation_error(self):
        """Test safe pipeline returns error dict instead of raising"""
        result = execute_pipeline_safe("", "Boston")

        assert "error" in result
        assert result["error"]["code"] == "VALIDATION_ERROR"

    @patch('src.pipeline.retrieve_route')
    @patch('src.pipeline.validate_request')
    def test_safe_pipeline_returns_error_dict_on_route_error(
        self,
        mock_validate,
        mock_retrieve,
        transaction_context
    ):
        """Test safe pipeline handles route errors gracefully"""
        mock_validate.return_value = transaction_context
        mock_retrieve.side_effect = RouteRetrievalError("Not found")

        result = execute_pipeline_safe("New York", "InvalidPlace")

        assert "error" in result
        assert result["error"]["code"] == "ROUTE_NOT_FOUND"

    @patch('src.pipeline.Orchestrator')
    @patch('src.pipeline.retrieve_route')
    @patch('src.pipeline.validate_request')
    def test_safe_pipeline_handles_unexpected_errors(
        self,
        mock_validate,
        mock_retrieve,
        mock_orchestrator_class,
        transaction_context,
        sample_route_data
    ):
        """Test safe pipeline handles unexpected errors"""
        mock_validate.return_value = transaction_context
        mock_retrieve.return_value = sample_route_data

        mock_orchestrator = MagicMock()
        mock_orchestrator.enrich_route.side_effect = RuntimeError("Unexpected error")
        mock_orchestrator_class.return_value = mock_orchestrator

        result = execute_pipeline_safe("New York", "Boston")

        assert "error" in result
        assert result["error"]["code"] == "INTERNAL_ERROR"


@pytest.mark.unit
class TestErrorResponse:
    """Test ErrorResponse structure"""

    def test_error_response_creation(self):
        """Test creating error response"""
        from src.pipeline import ErrorResponse

        error = ErrorResponse(
            transaction_id="TXID-test",
            error_code="TEST_ERROR",
            message="Test error message"
        )

        result = error.to_dict()
        assert result["transaction_id"] == "TXID-test"
        assert result["error"]["code"] == "TEST_ERROR"
        assert result["error"]["message"] == "Test error message"
        assert "timestamp" in result
