import unittest
from datetime import timedelta
from src.ai.node_metrics import NodeMetricsCollector

class TestNodeMetricsCollector(unittest.TestCase):
    """Test cases for the NodeMetricsCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = NodeMetricsCollector()
    
    def test_determine_status(self):
        """Test determining node status from metrics."""
        # Test unknown status
        self.assertEqual(self.collector._determine_status({}, {}), 'unknown')
        
        # Test offline status (high CPU)
        stats = {
            'cpu_usage': {'mean': 96.0},
            'memory_usage': {'mean': 85.0}
        }
        self.assertEqual(self.collector._determine_status(stats, {}), 'offline')
        
        # Test offline status (high disk usage)
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0},
            'disk_usage': {'mean': 96.0}
        }
        self.assertEqual(self.collector._determine_status(stats, {}), 'offline')
        
        # Test degraded status (high CPU)
        stats = {
            'cpu_usage': {'mean': 85.0},
            'memory_usage': {'mean': 75.0}
        }
        self.assertEqual(self.collector._determine_status(stats, {}), 'degraded')
        
        # Test degraded status (high disk usage)
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0},
            'disk_usage': {'mean': 85.0}
        }
        self.assertEqual(self.collector._determine_status(stats, {}), 'degraded')
        
        # Test online status
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0},
            'disk_usage': {'mean': 70.0}
        }
        self.assertEqual(self.collector._determine_status(stats, {}), 'online')
    
    def test_determine_health(self):
        """Test determining node health from metrics."""
        # Test unknown health
        self.assertEqual(self.collector._determine_health({}, {}), 'unknown')
        
        # Test critical health (high CPU)
        stats = {
            'cpu_usage': {'mean': 95.0},
            'memory_usage': {'mean': 85.0}
        }
        self.assertEqual(self.collector._determine_health(stats, {}), 'critical')
        
        # Test critical health (high temperature)
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0},
            'temperature': {'mean': 85.0}
        }
        self.assertEqual(self.collector._determine_health(stats, {}), 'critical')
        
        # Test warning health (high CPU)
        stats = {
            'cpu_usage': {'mean': 75.0},
            'memory_usage': {'mean': 65.0}
        }
        self.assertEqual(self.collector._determine_health(stats, {}), 'warning')
        
        # Test warning health (high temperature)
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0},
            'temperature': {'mean': 75.0}
        }
        self.assertEqual(self.collector._determine_health(stats, {}), 'warning')
        
        # Test healthy status
        stats = {
            'cpu_usage': {'mean': 50.0},
            'memory_usage': {'mean': 60.0},
            'temperature': {'mean': 65.0}
        }
        self.assertEqual(self.collector._determine_health(stats, {}), 'healthy')
    
    def test_generate_alerts(self):
        """Test generating node-specific alerts."""
        # Test high CPU usage alert
        stats = {
            'cpu_usage': {'mean': 95.0}
        }
        trends = {}
        alerts = self.collector._generate_alerts(stats, trends)
        
        self.assertTrue(any(
            a['type'] == 'critical' and a['metric'] == 'cpu_usage'
            for a in alerts
        ))
        
        # Test high memory usage alert
        stats = {
            'memory_usage': {'mean': 95.0}
        }
        trends = {}
        alerts = self.collector._generate_alerts(stats, trends)
        
        self.assertTrue(any(
            a['type'] == 'critical' and a['metric'] == 'memory_usage'
            for a in alerts
        ))
        
        # Test low disk space alert
        stats = {
            'disk_usage': {'mean': 95.0}
        }
        trends = {}
        alerts = self.collector._generate_alerts(stats, trends)
        
        self.assertTrue(any(
            a['type'] == 'critical' and a['metric'] == 'disk_usage'
            for a in alerts
        ))
        
        # Test high temperature alert
        stats = {
            'temperature': {'mean': 85.0}
        }
        trends = {}
        alerts = self.collector._generate_alerts(stats, trends)
        
        self.assertTrue(any(
            a['type'] == 'critical' and a['metric'] == 'temperature'
            for a in alerts
        ))
    
    def test_analyze_metrics_integration(self):
        """Test the complete metrics analysis workflow."""
        # Add test metrics
        metrics = [
            {
                'cpu_usage': 50.0,
                'memory_usage': 60.0,
                'disk_usage': 70.0,
                'temperature': 65.0
            },
            {
                'cpu_usage': 60.0,
                'memory_usage': 70.0,
                'disk_usage': 75.0,
                'temperature': 70.0
            },
            {
                'cpu_usage': 70.0,
                'memory_usage': 80.0,
                'disk_usage': 80.0,
                'temperature': 75.0
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
        self.assertEqual(analysis['trends']['disk_usage'], 'increasing')
        self.assertEqual(analysis['trends']['temperature'], 'increasing')
        
        # Check alerts
        self.assertTrue(any(
            a['type'] == 'warning' and a['metric'] == 'temperature'
            for a in analysis['alerts']
        ))

if __name__ == '__main__':
    unittest.main() 