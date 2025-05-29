"""
Shared test fixtures for AI module tests.
"""
import pytest
from unittest.mock import Mock
from datetime import datetime

@pytest.fixture
def mock_exchange_client():
    """Create a mock ExchangeAPIClient with common attributes."""
    client = Mock()
    client.org_id = "test_org"
    client.credential_manager._credentials.org_id = "test_org"
    return client

@pytest.fixture
def mock_service_data():
    """Create mock service data for testing."""
    return {
        'id': 'test_service',
        'name': 'Test Service',
        'status': 'running',
        'deployment': {
            'resources': {
                'cpu': 1.0,
                'memory': 512.0
            }
        },
        'url': 'http://test.com'
    }

@pytest.fixture
def mock_node_data():
    """Create mock node data for testing."""
    return {
        'id': 'test_node',
        'name': 'Test Node',
        'status': {
            'resources': {
                'cpu': 50.0,
                'memory': 60.0,
                'disk': 70.0
            },
            'temperature': 45.0
        },
        'lastHeartbeat': datetime.now().isoformat()
    }

@pytest.fixture
def mock_metrics_data():
    """Create mock metrics data for testing."""
    return {
        'cpu_usage': 50.0,
        'memory_usage': 60.0,
        'disk_usage': 70.0,
        'response_time': 500.0,
        'error_rate': 0.01,
        'temperature': 45.0
    }

@pytest.fixture
def mock_analysis_result():
    """Create mock analysis result for testing."""
    return {
        'status': 'healthy',
        'health': 'good',
        'alerts': [],
        'recommendations': [],
        'metrics': {
            'cpu_usage': 50.0,
            'memory_usage': 60.0
        }
    } 