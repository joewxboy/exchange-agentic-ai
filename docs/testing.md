# Testing Documentation

This document provides an overview of the test suites in the project and how to run them.

## Test Structure

The test suite is organized into several modules:

- `tests/test_base_metrics.py`: Tests for the base metrics collection functionality
- `tests/test_base_agent.py`: Tests for the base AI agent functionality
- `tests/test_service_metrics.py`: Tests for service-specific metrics collection
- `tests/test_service_agent.py`: Tests for service management agent functionality

## Running Tests

To run all tests:
```bash
pytest
```

To run specific test modules:
```bash
pytest tests/test_base_metrics.py
pytest tests/test_base_agent.py
pytest tests/test_service_metrics.py
pytest tests/test_service_agent.py
```

To run tests with coverage:
```bash
pytest --cov=src tests/
```

## Test Suites

### Base Metrics Collector Tests (`test_base_metrics.py`)

Tests the core metrics collection functionality:

- **Initialization**: Verifies proper setup of metrics history and tracking
- **Metrics Management**:
  - Adding metrics to history
  - Retrieving recent metrics with time windows
  - Cleaning up old metrics
- **Statistics Calculation**:
  - Mean, min, max, and standard deviation
  - Handling of empty datasets
- **Trend Detection**:
  - Increasing trends
  - Decreasing trends
  - Stable trends
  - Insufficient data cases

### Base AI Agent Tests (`test_base_agent.py`)

Tests the core AI agent functionality:

- **Initialization**: Verifies proper setup of client and history
- **Logging System**:
  - Error logging
  - Info logging
  - Warning logging
- **History Management**:
  - Retrieving full history
  - Filtering history by type
  - Clearing history
- **Abstract Methods**:
  - Analyze implementation
  - Act implementation
- **Timestamp Generation**: Verifies proper datetime handling

### Service Metrics Tests (`test_service_metrics.py`)

Tests the service-specific metrics collection:

- **Container Metrics**:
  - CPU usage monitoring
  - Memory usage tracking
  - Process statistics
- **Response Time Measurement**:
  - Successful requests
  - Failed requests
  - Timeout handling
- **Error Rate Calculation**:
  - Historical error tracking
  - Rate computation
- **Health Analysis**:
  - Status determination
  - Alert generation
  - Recommendation creation

### Service Agent Tests (`test_service_agent.py`)

Tests the service management functionality:

- **Service Analysis**:
  - Empty service list handling
  - Multiple service analysis
  - Metrics integration
- **Action Management**:
  - Action type determination
  - Invalid action handling
  - Service scaling
  - Service updates
  - Service restarts
- **Error Handling**:
  - API failures
  - Invalid configurations
  - Resource constraints

## Test Fixtures

The test suites use several fixtures to provide common test resources:

- `metrics_collector`: Provides a test implementation of `BaseMetricsCollector`
- `mock_process`: Creates a mock process for container metrics testing
- `mock_client`: Provides a mock Exchange API client
- `service_agent`: Creates a test instance of `ServiceManagementAgent`

## Best Practices

1. **Isolation**: Each test should be independent and not rely on the state from other tests
2. **Mocking**: External dependencies are mocked to ensure reliable testing
3. **Coverage**: Tests cover both success and failure scenarios
4. **Edge Cases**: Special attention is paid to boundary conditions and error cases
5. **Async Testing**: Proper handling of asynchronous operations using `pytest.mark.asyncio`

## Adding New Tests

When adding new tests:

1. Place them in the appropriate test module
2. Use existing fixtures when possible
3. Follow the established naming conventions
4. Include docstrings explaining the test purpose
5. Ensure proper cleanup in teardown if needed

## Continuous Integration

The test suite is integrated into the CI pipeline and runs on every pull request. The pipeline:

1. Runs all tests
2. Generates coverage reports
3. Fails if any tests fail
4. Fails if coverage drops below thresholds 