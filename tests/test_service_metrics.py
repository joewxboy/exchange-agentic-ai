"""
Tests for the ServiceMetricsCollector class.
"""
import pytest
from datetime import datetime, timedelta
import psutil
import requests
from unittest.mock import patch, MagicMock
from src.ai.service_metrics import ServiceMetricsCollector

@pytest.fixture
def metrics_collector():
    """Create a ServiceMetricsCollector instance for testing."""
    return ServiceMetricsCollector()

@pytest.fixture
def mock_process():
    """Create a mock process for testing."""
    process = MagicMock()
    process.cpu_percent.return_value = 50.0
    process.memory_percent.return_value = 60.0
    process.memory_info.return_value = MagicMock(rss=1024 * 1024 * 100)  # 100MB
    process.num_threads.return_value = 4
    process.open_files.return_value = [MagicMock()]
    process.connections.return_value = [MagicMock()]
    return process

def test_init(metrics_collector):
    """Test initialization of ServiceMetricsCollector."""
    assert metrics_collector._metrics_history == {}
    assert metrics_collector._last_check == {}
    assert metrics_collector._response_times == {}

@patch('psutil.process_iter')
def test_get_container_metrics(mock_process_iter, metrics_collector, mock_process):
    """Test getting container metrics."""
    # Mock process iteration
    mock_process_iter.return_value = [
        MagicMock(info={'pid': 123, 'name': 'test', 'cmdline': ['test-service']})
    ]
    
    # Mock Process creation
    with patch('psutil.Process', return_value=mock_process):
        metrics = metrics_collector._get_container_metrics('test-service')
        
        assert metrics['cpu_usage'] == 50.0
        assert metrics['memory_usage'] == 60.0
        assert metrics['memory_rss'] == 100.0  # MB
        assert metrics['threads'] == 4
        assert metrics['open_files'] == 1
        assert metrics['connections'] == 1

@patch('requests.get')
def test_measure_response_time(mock_get, metrics_collector):
    """Test measuring response time."""
    # Mock successful response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response
    
    response_time = metrics_collector._measure_response_time('test-service', 'http://test.com')
    assert isinstance(response_time, float)
    assert response_time >= 0

@patch('requests.get')
def test_measure_response_time_error(mock_get, metrics_collector):
    """Test measuring response time with error."""
    # Mock failed response
    mock_get.side_effect = requests.RequestException()
    
    response_time = metrics_collector._measure_response_time('test-service', 'http://test.com')
    assert response_time == float('inf')

def test_calculate_error_rate(metrics_collector):
    """Test calculating error rate."""
    service_id = 'test-service'
    
    # Test with no history
    assert metrics_collector._calculate_error_rate(service_id) == 0.0
    
    # Add some metrics with errors
    metrics_collector._metrics_history[service_id] = [
        {'error': True},
        {'error': False},
        {'error': True}
    ]
    
    error_rate = metrics_collector._calculate_error_rate(service_id)
    assert error_rate == pytest.approx(0.666, 0.001)

def test_collect_metrics(metrics_collector):
    """Test collecting metrics."""
    service_id = 'test-service'
    service_data = {'url': 'http://test.com'}
    
    with patch.object(metrics_collector, '_get_container_metrics') as mock_container_metrics, \
         patch.object(metrics_collector, '_measure_response_time') as mock_response_time, \
         patch.object(metrics_collector, '_calculate_error_rate') as mock_error_rate:
        
        mock_container_metrics.return_value = {
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'memory_rss': 100.0,
            'threads': 4,
            'open_files': 1,
            'connections': 1
        }
        mock_response_time.return_value = 100.0
        mock_error_rate.return_value = 0.1
        
        metrics = metrics_collector.collect_metrics(service_id, service_data)
        
        assert metrics['cpu_usage'] == 50.0
        assert metrics['memory_usage'] == 60.0
        assert metrics['memory_rss'] == 100.0
        assert metrics['response_time'] == 100.0
        assert metrics['error_rate'] == 0.1
        assert isinstance(metrics['timestamp'], datetime)

def test_cleanup_old_metrics(metrics_collector):
    """Test cleaning up old metrics."""
    service_id = 'test-service'
    max_history = 5
    
    # Add more metrics than max_history
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': datetime.now()} for _ in range(10)
    ]
    
    metrics_collector._cleanup_old_metrics(service_id, max_history)
    assert len(metrics_collector._metrics_history[service_id]) == max_history

def test_get_metrics_history(metrics_collector):
    """Test getting metrics history."""
    service_id = 'test-service'
    now = datetime.now()
    
    # Add metrics with different timestamps
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': now - timedelta(minutes=30)},
        {'timestamp': now - timedelta(minutes=45)},
        {'timestamp': now - timedelta(minutes=90)}
    ]
    
    # Get metrics from last hour
    recent_metrics = metrics_collector.get_metrics_history(service_id, window_minutes=60)
    assert len(recent_metrics) == 2

def test_analyze_metrics(metrics_collector):
    """Test analyzing metrics."""
    service_id = 'test-service'
    
    # Add some test metrics
    metrics_collector._metrics_history[service_id] = [
        {
            'timestamp': datetime.now(),
            'cpu_usage': 85.0,
            'memory_usage': 75.0,
            'response_time': 1500.0,
            'error_rate': 0.06
        }
    ]
    
    analysis = metrics_collector.analyze_metrics(service_id)
    
    assert analysis['status'] == 'warning'
    assert analysis['health'] == 'good'
    assert len(analysis['alerts']) > 0
    assert len(analysis['recommendations']) > 0
    assert 'metrics' in analysis

def test_analyze_metrics_critical(metrics_collector):
    """Test analyzing metrics with critical conditions."""
    service_id = 'test-service'
    
    # Add metrics with critical values
    metrics_collector._metrics_history[service_id] = [
        {
            'timestamp': datetime.now(),
            'cpu_usage': 95.0,
            'memory_usage': 95.0,
            'response_time': 2500.0,
            'error_rate': 0.15
        }
    ]
    
    analysis = metrics_collector.analyze_metrics(service_id)
    
    assert analysis['status'] == 'critical'
    assert analysis['health'] == 'poor'
    assert any('Critical' in alert for alert in analysis['alerts'])
    assert any('Immediate' in rec for rec in analysis['recommendations'])

def test_analyze_metrics_no_history(metrics_collector):
    """Test analyzing metrics with no history."""
    service_id = 'test-service'
    
    analysis = metrics_collector.analyze_metrics(service_id)
    
    assert analysis['status'] == 'unknown'
    assert analysis['health'] == 'unknown'
    assert len(analysis['alerts']) == 0
    assert len(analysis['recommendations']) == 0

if __name__ == '__main__':
    pytest.main() 