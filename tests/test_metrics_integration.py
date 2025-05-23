import unittest
from datetime import datetime, timedelta
from src.ai.metrics import MetricsCollector
from src.ai.service_metrics import ServiceMetricsCollector
from src.ai.node_metrics import NodeMetricsCollector
from src.ai.service_agent import ServiceManagementAgent
from src.ai.node_agent import NodeManagementAgent
from src.exchange.client import ExchangeAPIClient
import os
import asyncio

class TestMetricsIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment with API client and agents."""
        # Initialize API client with test credentials
        cls.client = ExchangeAPIClient(
            base_url=os.getenv("EXCHANGE_URL", "http://localhost:8080"),
            org=os.getenv("EXCHANGE_ORG", "testorg"),
            username=os.getenv("EXCHANGE_USERNAME", "testuser"),
            password=os.getenv("EXCHANGE_PASSWORD", "testpass")
        )
        
        # Initialize agents
        cls.service_agent = ServiceManagementAgent(cls.client)
        cls.node_agent = NodeManagementAgent(cls.client)
        
        # Initialize metrics collectors
        cls.service_metrics = ServiceMetricsCollector()
        cls.node_metrics = NodeMetricsCollector()

    def setUp(self):
        """Set up test data before each test."""
        # Sample service metrics
        self.service_metrics_data = {
            'cpu_usage': 65.5,
            'memory_usage': 72.3,
            'error_rate': 0.03,
            'response_time': 250.0,
            'timestamp': datetime.now()
        }
        
        # Sample node metrics
        self.node_metrics_data = {
            'cpu_usage': 45.5,
            'memory_usage': 62.3,
            'disk_usage': 75.8,
            'temperature': 65.0,
            'timestamp': datetime.now()
        }

    async def test_service_metrics_collection_and_analysis(self):
        """Test service metrics collection and analysis integration."""
        # Add metrics to collector
        self.service_metrics.add_metrics(self.service_metrics_data)
        
        # Get recent metrics
        recent_metrics = self.service_metrics.get_recent_metrics()
        self.assertGreater(len(recent_metrics), 0)
        
        # Analyze metrics
        analysis = self.service_metrics.analyze_metrics(recent_metrics)
        
        # Verify analysis results
        self.assertIn('status', analysis)
        self.assertIn('health', analysis)
        self.assertIn('trends', analysis)
        self.assertIn('alerts', analysis)
        self.assertIn('statistics', analysis)
        
        # Verify status values
        self.assertIn(analysis['status'], ['running', 'degraded', 'failed', 'unknown'])
        
        # Verify health values
        self.assertIn(analysis['health'], ['healthy', 'warning', 'critical', 'unknown'])

    async def test_node_metrics_collection_and_analysis(self):
        """Test node metrics collection and analysis integration."""
        # Add metrics to collector
        self.node_metrics.add_metrics(self.node_metrics_data)
        
        # Get recent metrics
        recent_metrics = self.node_metrics.get_recent_metrics()
        self.assertGreater(len(recent_metrics), 0)
        
        # Analyze metrics
        analysis = self.node_metrics.analyze_metrics(recent_metrics)
        
        # Verify analysis results
        self.assertIn('status', analysis)
        self.assertIn('health', analysis)
        self.assertIn('trends', analysis)
        self.assertIn('alerts', analysis)
        self.assertIn('statistics', analysis)
        
        # Verify status values
        self.assertIn(analysis['status'], ['online', 'degraded', 'offline', 'unknown'])
        
        # Verify health values
        self.assertIn(analysis['health'], ['healthy', 'warning', 'critical', 'unknown'])

    async def test_service_agent_metrics_integration(self):
        """Test integration between service agent and metrics collector."""
        # Add metrics to collector
        self.service_metrics.add_metrics(self.service_metrics_data)
        
        # Analyze service state
        analysis = await self.service_agent.analyze()
        
        # Verify analysis results
        self.assertIn('services', analysis)
        self.assertIn('recommendations', analysis)
        self.assertIn('metrics', analysis)
        
        # Verify metrics in analysis
        self.assertIn('cpu_usage', analysis['metrics'])
        self.assertIn('memory_usage', analysis['metrics'])
        self.assertIn('error_rate', analysis['metrics'])

    async def test_node_agent_metrics_integration(self):
        """Test integration between node agent and metrics collector."""
        # Add metrics to collector
        self.node_metrics.add_metrics(self.node_metrics_data)
        
        # Analyze node state
        analysis = await self.node_agent.analyze()
        
        # Verify analysis results
        self.assertIn('nodes', analysis)
        self.assertIn('recommendations', analysis)
        self.assertIn('metrics', analysis)
        
        # Verify metrics in analysis
        self.assertIn('cpu_usage', analysis['metrics'])
        self.assertIn('memory_usage', analysis['metrics'])
        self.assertIn('disk_usage', analysis['metrics'])
        self.assertIn('temperature', analysis['metrics'])

    async def test_metrics_history_cleanup(self):
        """Test metrics history cleanup functionality."""
        # Add metrics with old timestamp
        old_metrics = self.service_metrics_data.copy()
        old_metrics['timestamp'] = datetime.now() - timedelta(hours=2)
        self.service_metrics.add_metrics(old_metrics)
        
        # Add current metrics
        self.service_metrics.add_metrics(self.service_metrics_data)
        
        # Get recent metrics (should only include current metrics)
        recent_metrics = self.service_metrics.get_recent_metrics(timedelta(minutes=30))
        self.assertEqual(len(recent_metrics), 1)

    async def test_alert_generation(self):
        """Test alert generation with critical metrics."""
        # Add critical metrics
        critical_metrics = {
            'cpu_usage': 95.0,
            'memory_usage': 98.0,
            'error_rate': 0.15,
            'response_time': 2000.0,
            'timestamp': datetime.now()
        }
        self.service_metrics.add_metrics(critical_metrics)
        
        # Analyze metrics
        analysis = self.service_metrics.analyze_metrics(
            self.service_metrics.get_recent_metrics()
        )
        
        # Verify alerts
        self.assertGreater(len(analysis['alerts']), 0)
        self.assertEqual(analysis['health'], 'critical')

    def test_metrics_collector_configuration(self):
        """Test metrics collector configuration."""
        # Test custom analysis window
        custom_window = timedelta(minutes=45)
        collector = ServiceMetricsCollector(analysis_window=custom_window)
        self.assertEqual(collector._analysis_window, custom_window)
        
        # Test default analysis window
        collector = ServiceMetricsCollector()
        self.assertEqual(collector._analysis_window, timedelta(minutes=15))

def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

if __name__ == '__main__':
    unittest.main() 