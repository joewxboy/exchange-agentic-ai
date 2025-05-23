import unittest
from datetime import timedelta
from src.ai.service_metrics import ServiceMetricsCollector

class TestServiceMetricsCollector(unittest.TestCase):
    """Test cases for the ServiceMetricsCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = ServiceMetricsCollector()
    
    def test_determine_status(self):
        """Test determining service status from metrics."""
        # Test unknown status
        self.assertEqual(self.collector._determine_status({}, {}), 'unknown')
        
        # Test failed status
        stats = {
            'cpu_usage': {'mean': 95.0},
            'memory_usage': {'mean': 85.0}
        }
        self.assertEqual(self.collector._determine_status(stats, {}), 'failed')
        
        # Test degraded status
        stats = {
            'cpu_usage': {'mean': 75.0},
            'memory_usage': {'mean': 65.0}
        }
        self.assertEqual(self.collector._determine_status(stats, {}), 'degraded')
        
        # Test running status
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0}
        }
        self.assertEqual(self.collector._determine_status(stats, {}), 'running')
    
    def test_determine_health(self):
        """Test determining service health from metrics."""
        # Test unknown health
        self.assertEqual(self.collector._determine_health({}, {}), 'unknown')
        
        # Test critical health (high error rate)
        stats = {
            'error_rate': {'mean': 0.15}
        }
        self.assertEqual(self.collector._determine_health(stats, {}), 'critical')
        
        # Test warning health (moderate error rate)
        stats = {
            'error_rate': {'mean': 0.07}
        }
        self.assertEqual(self.collector._determine_health(stats, {}), 'warning')
        
        # Test warning health (increasing resource usage)
        stats = {
            'error_rate': {'mean': 0.01}
        }
        trends = {
            'cpu_usage': 'increasing',
            'memory_usage': 'stable'
        }
        self.assertEqual(self.collector._determine_health(stats, trends), 'warning')
        
        # Test healthy status
        stats = {
            'error_rate': {'mean': 0.01}
        }
        trends = {
            'cpu_usage': 'stable',
            'memory_usage': 'stable'
        }
        self.assertEqual(self.collector._determine_health(stats, trends), 'healthy')
    
    def test_generate_alerts(self):
        """Test generating service-specific alerts."""
        # Test high error rate alert
        stats = {
            'error_rate': {'mean': 0.15}
        }
        trends = {}
        alerts = self.collector._generate_alerts(stats, trends)
        
        self.assertTrue(any(
            a['type'] == 'critical' and a['metric'] == 'error_rate'
            for a in alerts
        ))
        
        # Test high response time alert
        stats = {
            'response_time': {'mean': 1500.0}
        }
        trends = {}
        alerts = self.collector._generate_alerts(stats, trends)
        
        self.assertTrue(any(
            a['type'] == 'warning' and a['metric'] == 'response_time'
            for a in alerts
        ))
    
    def test_analyze_metrics_integration(self):
        """Test the complete metrics analysis workflow."""
        # Add test metrics
        metrics = [
            {
                'cpu_usage': 50.0,
                'memory_usage': 60.0,
                'error_rate': 0.02,
                'response_time': 500.0
            },
            {
                'cpu_usage': 60.0,
                'memory_usage': 70.0,
                'error_rate': 0.03,
                'response_time': 600.0
            },
            {
                'cpu_usage': 70.0,
                'memory_usage': 80.0,
                'error_rate': 0.04,
                'response_time': 700.0
            }
        ]
        
        for metric in metrics:
            self.collector.add_metrics(metric)
        
        analysis = self.collector.analyze_metrics(self.collector.get_recent_metrics())
        
        # Check status and health
        self.assertEqual(analysis['status'], 'degraded')
        self.assertEqual(analysis['health'], 'warning')
        
        # Check trends
        self.assertEqual(analysis['trends']['cpu_usage'], 'increasing')
        self.assertEqual(analysis['trends']['memory_usage'], 'increasing')
        
        # Check alerts
        self.assertTrue(any(
            a['type'] == 'warning' and a['metric'] == 'response_time'
            for a in analysis['alerts']
        ))

if __name__ == '__main__':
    unittest.main() 