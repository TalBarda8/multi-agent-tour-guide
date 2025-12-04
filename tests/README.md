# Test Suite Documentation

## Overview

This directory contains comprehensive unit and integration tests for the Multi-Agent AI Tour Guide System. The test suite is designed to achieve 70-80% code coverage as per M.Sc. Computer Science submission guidelines.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # PyTest fixtures and configuration
├── test_models.py           # Data structure tests
├── test_config.py           # Configuration management tests
├── test_request_validator.py # Input validation tests
├── test_route_retrieval.py  # Google Maps integration tests
├── test_waypoint_preprocessor.py # Waypoint processing tests
├── test_pipeline.py         # End-to-end pipeline tests
├── test_orchestrator.py     # Agent orchestration and concurrency tests
├── test_mock_agents.py      # Mock agent implementation tests
├── test_response_formatter.py # Response formatting tests
└── README.md               # This file
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov=src --cov-report=term-missing
```

### Run Specific Test File
```bash
pytest tests/test_models.py
```

### Run Tests by Marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run with Verbose Output
```bash
pytest -v
```

## Test Coverage

The test suite aims for **70-80% code coverage** across all modules:

- **Models**: Data structures and helper functions (target: 80%+)
- **Configuration**: Config management and validation (target: 75%+)
- **Pipeline Modules**: All 6 pipeline stages (target: 70%+)
- **Google Maps Integration**: API client and parsing (target: 70%+)
- **Orchestrator**: Agent coordination logic (target: 70%+)

### Viewing Coverage Report

After running tests with coverage:
```bash
# View HTML report
open htmlcov/index.html

# View terminal report
pytest --cov=src --cov-report=term
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Test individual functions and classes in isolation
- Use mocks for external dependencies
- Fast execution (<100ms per test)
- Examples: `test_models.py`, `test_config.py`

### Integration Tests (`@pytest.mark.integration`)
- Test module interactions
- May use real dependencies
- Slower execution (100ms-1s per test)
- Examples: `test_pipeline.py`

### API Tests (`@pytest.mark.api`)
- Test external API integrations
- Require API keys or mock responses
- May be skipped in CI/CD
- Examples: `test_route_retrieval.py` (with real APIs)

### Slow Tests (`@pytest.mark.slow`)
- Tests that take >1s to execute
- Typically integration or API tests
- Can be skipped during development

## Test Fixtures

The `conftest.py` file provides reusable fixtures:

- `mock_config`: Test configuration with mock mode enabled
- `transaction_context`: Sample transaction context
- `sample_waypoint`: Sample waypoint data
- `sample_waypoints`: List of sample waypoints
- `sample_content_item`: Sample content item
- `sample_agent_result`: Sample agent result
- `sample_judge_decision`: Sample judge decision
- `sample_route_data`: Sample route data
- `mock_google_maps_response`: Mock Google Maps API response
- `mock_youtube_api_response`: Mock YouTube API response
- `mock_logger`: Mock logger for testing

## Writing New Tests

### Test Naming Convention
- Test files: `test_<module_name>.py`
- Test classes: `Test<Component>`
- Test functions: `test_<what_is_being_tested>`

### Example Test Structure
```python
@pytest.mark.unit
class TestMyComponent:
    """Test MyComponent functionality"""

    def test_successful_operation(self, mock_config):
        """Test that operation succeeds under normal conditions"""
        # Arrange
        component = MyComponent(mock_config)

        # Act
        result = component.do_something()

        # Assert
        assert result is not None
        assert result.status == "success"

    def test_error_handling(self):
        """Test that errors are handled gracefully"""
        component = MyComponent()

        with pytest.raises(MyException):
            component.do_invalid_operation()
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Expected Test Results

All tests should pass with the following characteristics:

- **Total Tests**: 92 tests across 9 test modules
- **Pass Rate**: 100% (all tests must pass)
- **Coverage**: 85% overall (exceeds target of 70-80%)
- **Execution Time**: ~24 seconds for full suite
- **No Warnings**: Clean test output without deprecation warnings

## Troubleshooting

### Common Issues

**Issue**: Import errors when running tests
```bash
# Solution: Install package in development mode
pip install -e .
```

**Issue**: Coverage not reporting correctly
```bash
# Solution: Ensure pytest-cov is installed
pip install pytest-cov
```

**Issue**: API tests failing
```bash
# Solution: Check that API keys are set in .env
# Or run in mock mode
export MOCK_MODE=true
pytest
```

## Best Practices

1. **Test Independence**: Each test should be independent and not rely on other tests
2. **Fixtures Over Setup**: Use pytest fixtures instead of setUp/tearDown methods
3. **Mock External Dependencies**: Always mock external APIs in unit tests
4. **Descriptive Names**: Test names should clearly describe what they test
5. **Arrange-Act-Assert**: Structure tests with clear setup, execution, and verification
6. **Edge Cases**: Test boundary conditions and error scenarios
7. **Fast Tests**: Keep unit tests fast (<100ms each)

## Resources

- [PyTest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)
