"""
Tests for the BaseMetricsCollector class.
"""
import pytest
from datetime import datetime, timedelta
from src.ai.metrics import BaseMetricsCollector

class TestMetricsCollector(BaseMetricsCollector):
    """Test implementation of BaseMetricsCollector."""
    def collect_metrics(self, service_id: str, service_data: dict) -> dict:
        """Test implementation of collect_metrics."""
        return {
            'timestamp': datetime.now(),
            'test_metric': 100.0
        }

@pytest.fixture
def metrics_collector():
    """Create a TestMetricsCollector instance for testing."""
    return TestMetricsCollector()

def test_init(metrics_collector):
    """Test initialization of BaseMetricsCollector."""
    assert hasattr(metrics_collector, '_metrics_history')
    assert hasattr(metrics_collector, '_last_check')
    assert hasattr(metrics_collector, '_response_times')

def test_add_metrics(metrics_collector):
    """Test adding metrics to history."""
    service_id = 'test-service'
    metrics = {
        'timestamp': datetime.now(),
        'test_metric': 100.0
    }
    
    metrics_collector.add_metrics(service_id, metrics)
    
    assert service_id in metrics_collector._metrics_history
    assert len(metrics_collector._metrics_history[service_id]) == 1
    assert metrics_collector._metrics_history[service_id][0] == metrics

def test_get_recent_metrics(metrics_collector):
    """Test getting recent metrics."""
    service_id = 'test-service'
    now = datetime.now()
    
    # Add metrics with different timestamps
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': now - timedelta(minutes=30), 'test_metric': 100.0},
        {'timestamp': now - timedelta(minutes=45), 'test_metric': 200.0},
        {'timestamp': now - timedelta(minutes=90), 'test_metric': 300.0}
    ]
    
    # Get metrics from last hour
    recent_metrics = metrics_collector.get_recent_metrics(service_id, window_minutes=60)
    assert len(recent_metrics) == 2
    assert all(m['test_metric'] in [100.0, 200.0] for m in recent_metrics)

def test_get_recent_metrics_no_history(metrics_collector):
    """Test getting recent metrics with no history."""
    service_id = 'test-service'
    recent_metrics = metrics_collector.get_recent_metrics(service_id)
    assert len(recent_metrics) == 0

def test_calculate_statistics(metrics_collector):
    """Test calculating statistics from metrics."""
    service_id = 'test-service'
    now = datetime.now()
    
    # Add metrics with different values
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': now, 'test_metric': 100.0},
        {'timestamp': now, 'test_metric': 200.0},
        {'timestamp': now, 'test_metric': 300.0}
    ]
    
    stats = metrics_collector.calculate_statistics(service_id, 'test_metric')
    
    assert stats['mean'] == 200.0
    assert stats['min'] == 100.0
    assert stats['max'] == 300.0
    assert stats['std'] == pytest.approx(81.65, 0.01)

def test_calculate_statistics_no_metrics(metrics_collector):
    """Test calculating statistics with no metrics."""
    service_id = 'test-service'
    stats = metrics_collector.calculate_statistics(service_id, 'test_metric')
    
    assert stats['mean'] == 0.0
    assert stats['min'] == 0.0
    assert stats['max'] == 0.0
    assert stats['std'] == 0.0

def test_detect_trends(metrics_collector):
    """Test detecting trends in metrics."""
    service_id = 'test-service'
    now = datetime.now()
    
    # Add metrics showing increasing trend
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': now - timedelta(minutes=30), 'test_metric': 100.0},
        {'timestamp': now - timedelta(minutes=20), 'test_metric': 200.0},
        {'timestamp': now - timedelta(minutes=10), 'test_metric': 300.0}
    ]
    
    trends = metrics_collector.detect_trends(service_id, 'test_metric')
    assert trends == 'increasing'
    
    # Add metrics showing decreasing trend
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': now - timedelta(minutes=30), 'test_metric': 300.0},
        {'timestamp': now - timedelta(minutes=20), 'test_metric': 200.0},
        {'timestamp': now - timedelta(minutes=10), 'test_metric': 100.0}
    ]
    
    trends = metrics_collector.detect_trends(service_id, 'test_metric')
    assert trends == 'decreasing'
    
    # Add metrics showing stable trend
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': now - timedelta(minutes=30), 'test_metric': 100.0},
        {'timestamp': now - timedelta(minutes=20), 'test_metric': 100.0},
        {'timestamp': now - timedelta(minutes=10), 'test_metric': 100.0}
    ]
    
    trends = metrics_collector.detect_trends(service_id, 'test_metric')
    assert trends == 'stable'

def test_detect_trends_insufficient_data(metrics_collector):
    """Test detecting trends with insufficient data."""
    service_id = 'test-service'
    now = datetime.now()
    
    # Add only one metric
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': now, 'test_metric': 100.0}
    ]
    
    trends = metrics_collector.detect_trends(service_id, 'test_metric')
    assert trends == 'unknown'

def test_cleanup_old_metrics(metrics_collector):
    """Test cleaning up old metrics."""
    service_id = 'test-service'
    max_history = 5
    
    # Add more metrics than max_history
    metrics_collector._metrics_history[service_id] = [
        {'timestamp': datetime.now()} for _ in range(10)
    ]
    
    metrics_collector.cleanup_old_metrics(service_id, max_history)
    assert len(metrics_collector._metrics_history[service_id]) == max_history

def test_cleanup_old_metrics_no_history(metrics_collector):
    """Test cleaning up old metrics with no history."""
    service_id = 'test-service'
    metrics_collector.cleanup_old_metrics(service_id)
    assert service_id not in metrics_collector._metrics_history 