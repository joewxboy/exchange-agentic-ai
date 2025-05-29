"""
Unit tests for the service metrics collector implementation.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import psutil
import requests
from src.ai.service_metrics import ServiceMetricsCollector

class TestServiceMetricsCollector:
    """Test cases for ServiceMetricsCollector."""
    
    @pytest.fixture
    def collector(self):
        """Create a test instance of ServiceMetricsCollector."""
        return ServiceMetricsCollector()
    
    @pytest.fixture
    def mock_process(self):
        """Create a mock process for psutil."""
        process = Mock()
        process.cpu_percent.return_value = 50.0
        process.memory_percent.return_value = 60.0
        process.memory_info.return_value = Mock(rss=1024 * 1024 * 100)  # 100MB
        process.num_threads.return_value = 4
        process.open_files.return_value = [Mock()]
        process.connections.return_value = [Mock()]
        return process
    
    def test_initialization(self):
        """Test collector initialization."""
        collector = ServiceMetricsCollector()
        assert collector.thresholds['cpu_warning'] == 80
        assert collector.thresholds['cpu_critical'] == 90
        assert collector.thresholds['memory_warning'] == 80
        assert collector.thresholds['memory_critical'] == 90
    
    def test_initialization_with_config(self):
        """Test collector initialization with custom thresholds."""
        config = {
            'cpu_warning_threshold': 70,
            'cpu_critical_threshold': 85,
            'memory_warning_threshold': 75,
            'memory_critical_threshold': 85
        }
        collector = ServiceMetricsCollector(config)
        assert collector.thresholds['cpu_warning'] == 70
        assert collector.thresholds['cpu_critical'] == 85
        assert collector.thresholds['memory_warning'] == 75
        assert collector.thresholds['memory_critical'] == 85
    
    @patch('psutil.process_iter')
    def test_get_container_metrics(self, mock_process_iter, collector, mock_process):
        """Test container metrics collection."""
        mock_process_iter.return_value = [
            Mock(info={'pid': 123, 'name': 'test', 'cmdline': ['test_service']})
        ]
        
        with patch('psutil.Process', return_value=mock_process):
            metrics = collector._get_container_metrics('test_service')
            assert metrics['cpu_usage'] == 50.0
            assert metrics['memory_usage'] == 60.0
            assert metrics['memory_rss'] == 100.0
            assert metrics['threads'] == 4
            assert metrics['open_files'] == 1
            assert metrics['connections'] == 1
    
    @patch('psutil.process_iter')
    def test_get_container_metrics_no_process(self, mock_process_iter, collector):
        """Test container metrics collection when process not found."""
        mock_process_iter.return_value = []
        metrics = collector._get_container_metrics('test_service')
        assert metrics == {}
    
    @patch('requests.get')
    def test_measure_response_time(self, mock_get, collector):
        """Test response time measurement."""
        mock_get.return_value = Mock(status_code=200)
        response_time = collector._measure_response_time('test_service', 'http://test.com')
        assert isinstance(response_time, float)
        assert response_time > 0
    
    @patch('requests.get')
    def test_measure_response_time_error(self, mock_get, collector):
        """Test response time measurement with error."""
        mock_get.side_effect = requests.RequestException()
        response_time = collector._measure_response_time('test_service', 'http://test.com')
        assert response_time == float('inf')
    
    def test_calculate_error_rate(self, collector):
        """Test error rate calculation."""
        collector._request_counts['test_service'] = 100
        collector._error_counts['test_service'] = 5
        error_rate = collector._calculate_error_rate('test_service')
        assert error_rate == 0.05
    
    def test_calculate_error_rate_no_requests(self, collector):
        """Test error rate calculation with no requests."""
        error_rate = collector._calculate_error_rate('test_service')
        assert error_rate == 0.0
    
    def test_analyze_entity_metrics_healthy(self, collector):
        """Test metrics analysis for healthy service."""
        metrics = {
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'response_time': 500.0,
            'error_rate': 0.01
        }
        analysis = collector._analyze_entity_metrics(metrics)
        assert analysis['status'] == 'healthy'
        assert analysis['health'] == 'good'
        assert len(analysis['alerts']) == 0
    
    def test_analyze_entity_metrics_warning(self, collector):
        """Test metrics analysis for service with warnings."""
        metrics = {
            'cpu_usage': 85.0,
            'memory_usage': 85.0,
            'response_time': 1500.0,
            'error_rate': 0.06
        }
        analysis = collector._analyze_entity_metrics(metrics)
        assert analysis['status'] == 'warning'
        assert len(analysis['alerts']) > 0
        assert len(analysis['recommendations']) > 0
    
    def test_analyze_entity_metrics_critical(self, collector):
        """Test metrics analysis for service with critical issues."""
        metrics = {
            'cpu_usage': 95.0,
            'memory_usage': 95.0,
            'response_time': 2500.0,
            'error_rate': 0.15
        }
        analysis = collector._analyze_entity_metrics(metrics)
        assert analysis['status'] == 'critical'
        assert analysis['health'] == 'poor'
        assert len(analysis['alerts']) > 0
        assert len(analysis['recommendations']) > 0 