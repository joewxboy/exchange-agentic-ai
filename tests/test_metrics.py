import unittest
from datetime import datetime, timedelta
from src.ai.metrics import MetricsCollector

class TestMetricsCollector(unittest.TestCase):
    """Test cases for the base MetricsCollector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = MetricsCollector()
    
    def test_add_metrics(self):
        """Test adding metrics to the collector."""
        metrics = {
            'cpu_usage': 50.0,
            'memory_usage': 75.0,
            'error_rate': 0.02
        }
        
        self.collector.add_metrics(metrics)
        recent_metrics = self.collector.get_recent_metrics()
        
        self.assertEqual(len(recent_metrics), 1)
        self.assertEqual(recent_metrics[0]['data'], metrics)
        self.assertIn('timestamp', recent_metrics[0])
    
    def test_get_recent_metrics(self):
        """Test getting metrics within a time window."""
        # Add metrics with different timestamps
        old_metrics = {'value': 1.0}
        new_metrics = {'value': 2.0}
        
        self.collector.add_metrics(old_metrics)
        self.collector.add_metrics(new_metrics)
        
        # Get metrics from last minute
        recent = self.collector.get_recent_metrics(timedelta(minutes=1))
        self.assertEqual(len(recent), 2)
        
        # Get metrics from last second
        very_recent = self.collector.get_recent_metrics(timedelta(seconds=1))
        self.assertEqual(len(very_recent), 1)
        self.assertEqual(very_recent[0]['data'], new_metrics)
    
    def test_analyze_metrics(self):
        """Test analyzing metrics."""
        # Add some test metrics
        metrics = [
            {'cpu_usage': 50.0, 'memory_usage': 60.0},
            {'cpu_usage': 60.0, 'memory_usage': 70.0},
            {'cpu_usage': 70.0, 'memory_usage': 80.0}
        ]
        
        for metric in metrics:
            self.collector.add_metrics(metric)
        
        analysis = self.collector.analyze_metrics(self.collector.get_recent_metrics())
        
        # Check analysis structure
        self.assertIn('status', analysis)
        self.assertIn('health', analysis)
        self.assertIn('trends', analysis)
        self.assertIn('alerts', analysis)
        self.assertIn('statistics', analysis)
        
        # Check statistics
        stats = analysis['statistics']
        self.assertIn('cpu_usage', stats)
        self.assertIn('memory_usage', stats)
        
        # Check trends
        trends = analysis['trends']
        self.assertIn('cpu_usage', trends)
        self.assertIn('memory_usage', trends)
        self.assertEqual(trends['cpu_usage'], 'increasing')
        self.assertEqual(trends['memory_usage'], 'increasing')
    
    def test_extract_numeric_values(self):
        """Test extracting numeric values from metrics."""
        metrics = [
            {'cpu_usage': 50.0, 'status': 'running'},
            {'cpu_usage': 60.0, 'status': 'running'},
            {'cpu_usage': 70.0, 'status': 'running'}
        ]
        
        numeric_values = self.collector._extract_numeric_values(metrics)
        
        self.assertIn('cpu_usage', numeric_values)
        self.assertEqual(len(numeric_values['cpu_usage']), 3)
        self.assertNotIn('status', numeric_values)
    
    def test_calculate_statistics(self):
        """Test calculating statistics from numeric values."""
        numeric_values = {
            'metric1': [1.0, 2.0, 3.0, 4.0, 5.0],
            'metric2': [10.0, 20.0, 30.0]
        }
        
        stats = self.collector._calculate_statistics(numeric_values)
        
        self.assertIn('metric1', stats)
        self.assertIn('metric2', stats)
        
        # Check metric1 statistics
        metric1_stats = stats['metric1']
        self.assertEqual(metric1_stats['mean'], 3.0)
        self.assertEqual(metric1_stats['median'], 3.0)
        self.assertEqual(metric1_stats['min'], 1.0)
        self.assertEqual(metric1_stats['max'], 5.0)
    
    def test_analyze_trends(self):
        """Test analyzing trends in metrics."""
        metrics = [
            {'value': 1.0},
            {'value': 2.0},
            {'value': 3.0},
            {'value': 4.0},
            {'value': 5.0}
        ]
        
        trends = self.collector._analyze_trends(metrics)
        
        self.assertIn('value', trends)
        self.assertEqual(trends['value'], 'increasing')
    
    def test_generate_alerts(self):
        """Test generating alerts from statistics and trends."""
        stats = {
            'metric1': {
                'mean': 100.0,
                'std_dev': 60.0,  # High variance
                'max': 250.0  # Extreme value
            }
        }
        trends = {'metric1': 'stable'}
        
        alerts = self.collector._generate_alerts(stats, trends)
        
        self.assertEqual(len(alerts), 2)
        self.assertTrue(any(a['type'] == 'high_variance' for a in alerts))
        self.assertTrue(any(a['type'] == 'extreme_value' for a in alerts))

if __name__ == '__main__':
    unittest.main() 