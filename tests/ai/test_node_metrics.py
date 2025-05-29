"""
Unit tests for the node metrics collector implementation.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from src.ai.node_metrics import NodeMetricsCollector

class TestNodeMetricsCollector:
    """Test cases for NodeMetricsCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create a test instance of NodeMetricsCollector."""
        return NodeMetricsCollector()
    
    def test_initialization(self):
        """Test collector initialization."""
        collector = NodeMetricsCollector()
        assert collector.thresholds['cpu_warning'] == 70
        assert collector.thresholds['cpu_critical'] == 90
        assert collector.thresholds['memory_warning'] == 70
        assert collector.thresholds['memory_critical'] == 90
        assert collector.thresholds['disk_warning'] == 80
        assert collector.thresholds['disk_critical'] == 95
    
    def test_initialization_with_config(self):
        """Test collector initialization with custom thresholds."""
        config = {
            'cpu_warning_threshold': 60,
            'cpu_critical_threshold': 80,
            'memory_warning_threshold': 65,
            'memory_critical_threshold': 85,
            'disk_warning_threshold': 75,
            'disk_critical_threshold': 90
        }
        collector = NodeMetricsCollector(config)
        assert collector.thresholds['cpu_warning'] == 60
        assert collector.thresholds['cpu_critical'] == 80
        assert collector.thresholds['memory_warning'] == 65
        assert collector.thresholds['memory_critical'] == 85
        assert collector.thresholds['disk_warning'] == 75
        assert collector.thresholds['disk_critical'] == 90
    
    def test_collect_entity_metrics(self, collector):
        """Test metrics collection from node data."""
        node_id = "test_node"
        node_data = {
            'status': {
                'resources': {
                    'cpu': 50.0,
                    'memory': 60.0,
                    'disk': 70.0
                },
                'temperature': 45.0
            },
            'metrics': {
                'network_usage': 30.0
            }
        }
        
        metrics = collector._collect_entity_metrics(node_id, node_data)
        assert metrics['cpu_usage'] == 50.0
        assert metrics['memory_usage'] == 60.0
        assert metrics['disk_usage'] == 70.0
        assert metrics['temperature'] == 45.0
        assert metrics['network_usage'] == 30.0
    
    def test_collect_entity_metrics_missing_data(self, collector):
        """Test metrics collection with missing data."""
        node_id = "test_node"
        node_data = {}
        
        metrics = collector._collect_entity_metrics(node_id, node_data)
        assert metrics['cpu_usage'] == 0.0
        assert metrics['memory_usage'] == 0.0
        assert metrics['disk_usage'] == 0.0
        assert metrics['temperature'] == 0.0
    
    def test_calculate_statistics(self, collector):
        """Test statistics calculation."""
        metrics = {
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'disk_usage': 70.0,
            'temperature': 45.0
        }
        
        stats = collector._calculate_statistics(metrics)
        assert 'cpu_usage' in stats
        assert 'memory_usage' in stats
        assert 'disk_usage' in stats
        assert 'temperature' in stats
        
        for metric in stats.values():
            assert 'mean' in metric
            assert 'min' in metric
            assert 'max' in metric
    
    def test_determine_trends(self, collector):
        """Test trend determination."""
        # Add some history
        collector.metrics_history = [
            {'timestamp': datetime.now() - timedelta(minutes=5), 'cpu_usage': 40.0},
            {'timestamp': datetime.now() - timedelta(minutes=2), 'cpu_usage': 45.0}
        ]
        
        metrics = {'cpu_usage': 50.0}
        trends = collector._determine_trends(metrics)
        assert trends['cpu_usage'] == 'increasing'
    
    def test_determine_status_online(self, collector):
        """Test status determination for online node."""
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0},
            'disk_usage': {'mean': 70.0}
        }
        trends = {}
        
        status = collector._determine_status(stats, trends)
        assert status == 'online'
    
    def test_determine_status_degraded(self, collector):
        """Test status determination for degraded node."""
        stats = {
            'cpu_usage': {'mean': 75.0},
            'memory_usage': {'mean': 75.0},
            'disk_usage': {'mean': 85.0}
        }
        trends = {}
        
        status = collector._determine_status(stats, trends)
        assert status == 'degraded'
    
    def test_determine_status_offline(self, collector):
        """Test status determination for offline node."""
        stats = {
            'cpu_usage': {'mean': 95.0},
            'memory_usage': {'mean': 95.0},
            'disk_usage': {'mean': 98.0}
        }
        trends = {}
        
        status = collector._determine_status(stats, trends)
        assert status == 'offline'
    
    def test_determine_health_healthy(self, collector):
        """Test health determination for healthy node."""
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0},
            'temperature': {'mean': 45.0}
        }
        trends = {}
        
        health = collector._determine_health(stats, trends)
        assert health == 'healthy'
    
    def test_determine_health_warning(self, collector):
        """Test health determination for node with warnings."""
        stats = {
            'cpu_usage': {'mean': 75.0},
            'memory_usage': {'mean': 75.0},
            'temperature': {'mean': 75.0}
        }
        trends = {}
        
        health = collector._determine_health(stats, trends)
        assert health == 'warning'
    
    def test_determine_health_critical(self, collector):
        """Test health determination for critical node."""
        stats = {
            'cpu_usage': {'mean': 95.0},
            'memory_usage': {'mean': 95.0},
            'temperature': {'mean': 85.0}
        }
        trends = {}
        
        health = collector._determine_health(stats, trends)
        assert health == 'critical'
    
    def test_generate_alerts(self, collector):
        """Test alert generation."""
        stats = {
            'cpu_usage': {'mean': 95.0},
            'memory_usage': {'mean': 95.0},
            'disk_usage': {'mean': 98.0},
            'temperature': {'mean': 85.0}
        }
        trends = {}
        
        alerts = collector._generate_alerts(stats, trends)
        assert len(alerts) > 0
        assert any(alert['type'] == 'critical' for alert in alerts)
        assert any(alert['type'] == 'warning' for alert in alerts) 