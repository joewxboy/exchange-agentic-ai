"""
Unit tests for the metrics collector implementation.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.ai.metrics import BaseMetricsCollector

class TestBaseMetricsCollector:
    """Test cases for BaseMetricsCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create a test instance of BaseMetricsCollector."""
        class TestCollector(BaseMetricsCollector):
            def _collect_entity_metrics(self, entity_id, entity_data):
                return {'test_metric': 1.0}
            
            def _analyze_entity_metrics(self, metrics):
                return {
                    'status': 'test',
                    'health': 'good',
                    'alerts': [],
                    'recommendations': []
                }
        
        return TestCollector()
    
    def test_initialization(self):
        """Test collector initialization."""
        class TestCollector(BaseMetricsCollector):
            def _collect_entity_metrics(self, entity_id, entity_data):
                return {'test_metric': 1.0}
            def _analyze_entity_metrics(self, metrics):
                return {
                    'status': 'test',
                    'health': 'good',
                    'alerts': [],
                    'recommendations': []
                }
        collector = TestCollector()
        assert collector.config == {}
        assert collector.metrics_history == []
    
    def test_initialization_with_config(self):
        """Test collector initialization with configuration."""
        config = {'test': 'config'}
        class TestCollector(BaseMetricsCollector):
            def _collect_entity_metrics(self, entity_id, entity_data):
                return {'test_metric': 1.0}
            def _analyze_entity_metrics(self, metrics):
                return {
                    'status': 'test',
                    'health': 'good',
                    'alerts': [],
                    'recommendations': []
                }
        collector = TestCollector(config)
        assert collector.config == config
    
    def test_collect_metrics(self, collector):
        """Test metrics collection."""
        entity_id = "test_entity"
        entity_data = {'test': 'data'}
        
        metrics = collector.collect_metrics(entity_id, entity_data)
        assert metrics['test_metric'] == 1.0
        assert 'timestamp' in metrics
        assert len(collector.metrics_history) == 1
    
    def test_collect_metrics_error(self, collector):
        """Test metrics collection with error handling."""
        entity_id = "test_entity"
        entity_data = {'test': 'data'}
        
        # Force an error in _collect_entity_metrics
        def mock_collect(*args, **kwargs):
            raise Exception("Test error")
        
        collector._collect_entity_metrics = mock_collect
        
        metrics = collector.collect_metrics(entity_id, entity_data)
        assert metrics == {}
    
    def test_get_metrics_history(self, collector):
        """Test metrics history retrieval."""
        # Add some test metrics
        collector.metrics_history = [
            {'timestamp': datetime.now() - timedelta(minutes=30), 'test': 1},
            {'timestamp': datetime.now() - timedelta(minutes=15), 'test': 2},
            {'timestamp': datetime.now(), 'test': 3}
        ]
        
        # Test without window
        history = collector.get_metrics_history()
        assert len(history) == 3
        
        # Test with window
        history = collector.get_metrics_history(window_minutes=20)
        assert len(history) == 2
    
    def test_analyze_metrics(self, collector):
        """Test metrics analysis."""
        metrics = {'test_metric': 1.0}
        analysis = collector.analyze_metrics(metrics)
        assert analysis['status'] == 'test'
        assert analysis['health'] == 'good'
        assert 'alerts' in analysis
        assert 'recommendations' in analysis
    
    def test_analyze_metrics_error(self, collector):
        """Test metrics analysis with error handling."""
        metrics = {'test_metric': 1.0}
        
        # Force an error in _analyze_entity_metrics
        def mock_analyze(*args, **kwargs):
            raise Exception("Test error")
        
        collector._analyze_entity_metrics = mock_analyze
        
        analysis = collector.analyze_metrics(metrics)
        assert analysis['status'] == 'unknown'
        assert analysis['health'] == 'unknown'
        assert len(analysis['alerts']) == 1
        assert analysis['alerts'][0]['type'] == 'error'
    
    def test_cleanup_old_metrics(self, collector):
        """Test cleanup of old metrics."""
        now = datetime.now()
        collector.metrics_history = [
            {'timestamp': now - timedelta(days=8), 'test': 1},
            {'timestamp': now - timedelta(days=6), 'test': 2},
            {'timestamp': now - timedelta(days=4), 'test': 3},
            {'timestamp': now - timedelta(days=2), 'test': 4},
            {'timestamp': now, 'test': 5}
        ]
        collector.cleanup_old_metrics(max_age=timedelta(days=7))
        # Only metrics within 7 days should remain (test 2, 3, 4, 5)
        assert len(collector.metrics_history) == 4
        assert all(m['test'] in (2, 3, 4, 5) for m in collector.metrics_history)
    
    def test_cleanup_old_metrics_error(self, collector):
        """Test cleanup of old metrics with error handling."""
        collector.metrics_history = [{'invalid': 'data'}]
        collector.cleanup_old_metrics()
        # The invalid entry remains, only error is logged
        assert len(collector.metrics_history) == 1
        assert 'invalid' in collector.metrics_history[0] 