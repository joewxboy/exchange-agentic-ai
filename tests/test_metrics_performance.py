import unittest
import time
import psutil
import os
import asyncio
from datetime import datetime, timedelta
from src.ai.metrics import MetricsCollector
from src.ai.service_metrics import ServiceMetricsCollector
from src.ai.node_metrics import NodeMetricsCollector
from src.ai.service_agent import ServiceManagementAgent
from src.ai.node_agent import NodeManagementAgent
from src.exchange.client import ExchangeAPIClient

class TestMetricsPerformance(unittest.TestCase):
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
        
        # Get initial memory usage
        cls.initial_memory = psutil.Process().memory_info().rss

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

    def test_metrics_collection_performance(self):
        """Test performance of metrics collection."""
        # Test adding multiple metrics
        start_time = time.time()
        num_metrics = 1000
        
        for _ in range(num_metrics):
            self.service_metrics.add_metrics(self.service_metrics_data)
            self.node_metrics.add_metrics(self.node_metrics_data)
        
        end_time = time.time()
        collection_time = end_time - start_time
        
        # Verify performance
        self.assertLess(collection_time, 1.0)  # Should take less than 1 second
        self.assertEqual(len(self.service_metrics.get_recent_metrics()), num_metrics)
        self.assertEqual(len(self.node_metrics.get_recent_metrics()), num_metrics)

    def test_metrics_analysis_performance(self):
        """Test performance of metrics analysis."""
        # Add test metrics
        num_metrics = 1000
        for _ in range(num_metrics):
            self.service_metrics.add_metrics(self.service_metrics_data)
            self.node_metrics.add_metrics(self.node_metrics_data)
        
        # Test service metrics analysis
        start_time = time.time()
        service_analysis = self.service_metrics.analyze_metrics(
            self.service_metrics.get_recent_metrics()
        )
        service_analysis_time = time.time() - start_time
        
        # Test node metrics analysis
        start_time = time.time()
        node_analysis = self.node_metrics.analyze_metrics(
            self.node_metrics.get_recent_metrics()
        )
        node_analysis_time = time.time() - start_time
        
        # Verify performance
        self.assertLess(service_analysis_time, 0.5)  # Should take less than 0.5 seconds
        self.assertLess(node_analysis_time, 0.5)  # Should take less than 0.5 seconds
        
        # Verify analysis results
        self.assertIn('status', service_analysis)
        self.assertIn('health', service_analysis)
        self.assertIn('trends', service_analysis)
        self.assertIn('alerts', service_analysis)
        self.assertIn('statistics', service_analysis)

    def test_memory_usage(self):
        """Test memory usage of metrics collectors."""
        # Add large number of metrics
        num_metrics = 10000
        for _ in range(num_metrics):
            self.service_metrics.add_metrics(self.service_metrics_data)
            self.node_metrics.add_metrics(self.node_metrics_data)
        
        # Get current memory usage
        current_memory = psutil.Process().memory_info().rss
        memory_increase = current_memory - self.initial_memory
        
        # Verify memory usage
        self.assertLess(memory_increase, 100 * 1024 * 1024)  # Should use less than 100MB
        
        # Test cleanup
        self.service_metrics._cleanup_old_metrics()
        self.node_metrics._cleanup_old_metrics()
        
        # Verify cleanup reduced memory usage
        after_cleanup_memory = psutil.Process().memory_info().rss
        self.assertLess(after_cleanup_memory, current_memory)

    def test_concurrent_metrics_collection(self):
        """Test concurrent metrics collection performance."""
        async def collect_metrics(collector, metrics_data, num_metrics):
            for _ in range(num_metrics):
                collector.add_metrics(metrics_data)
                await asyncio.sleep(0)  # Allow other tasks to run
        
        # Test concurrent collection
        num_metrics = 1000
        start_time = time.time()
        
        # Run concurrent collection
        loop = asyncio.get_event_loop()
        tasks = [
            collect_metrics(self.service_metrics, self.service_metrics_data, num_metrics),
            collect_metrics(self.node_metrics, self.node_metrics_data, num_metrics)
        ]
        loop.run_until_complete(asyncio.gather(*tasks))
        
        end_time = time.time()
        collection_time = end_time - start_time
        
        # Verify performance
        self.assertLess(collection_time, 2.0)  # Should take less than 2 seconds
        self.assertEqual(len(self.service_metrics.get_recent_metrics()), num_metrics)
        self.assertEqual(len(self.node_metrics.get_recent_metrics()), num_metrics)

    def test_metrics_cleanup_performance(self):
        """Test performance of metrics cleanup."""
        # Add metrics with different timestamps
        num_metrics = 1000
        for i in range(num_metrics):
            # Add metrics with timestamps spread over the last hour
            timestamp = datetime.now() - timedelta(minutes=i/num_metrics * 60)
            service_metrics = self.service_metrics_data.copy()
            node_metrics = self.node_metrics_data.copy()
            service_metrics['timestamp'] = timestamp
            node_metrics['timestamp'] = timestamp
            
            self.service_metrics.add_metrics(service_metrics)
            self.node_metrics.add_metrics(node_metrics)
        
        # Test cleanup performance
        start_time = time.time()
        self.service_metrics._cleanup_old_metrics()
        self.node_metrics._cleanup_old_metrics()
        cleanup_time = time.time() - start_time
        
        # Verify performance
        self.assertLess(cleanup_time, 0.5)  # Should take less than 0.5 seconds
        
        # Verify cleanup results
        recent_metrics = self.service_metrics.get_recent_metrics()
        self.assertLess(len(recent_metrics), num_metrics)  # Should have cleaned up old metrics

    def test_alert_generation_performance(self):
        """Test performance of alert generation."""
        # Add metrics with varying values to trigger alerts
        num_metrics = 1000
        for i in range(num_metrics):
            # Vary metrics to trigger different alerts
            service_metrics = self.service_metrics_data.copy()
            node_metrics = self.node_metrics_data.copy()
            
            service_metrics['cpu_usage'] = 50 + (i % 50)  # Vary between 50-100%
            service_metrics['error_rate'] = 0.01 + (i % 10) * 0.01  # Vary between 1-10%
            node_metrics['temperature'] = 60 + (i % 30)  # Vary between 60-90°C
            
            self.service_metrics.add_metrics(service_metrics)
            self.node_metrics.add_metrics(node_metrics)
        
        # Test alert generation performance
        start_time = time.time()
        service_alerts = self.service_metrics._generate_alerts(
            self.service_metrics._calculate_statistics(
                self.service_metrics._extract_numeric_values(
                    self.service_metrics.get_recent_metrics()
                )
            ),
            self.service_metrics._analyze_trends(
                self.service_metrics.get_recent_metrics()
            )
        )
        node_alerts = self.node_metrics._generate_alerts(
            self.node_metrics._calculate_statistics(
                self.node_metrics._extract_numeric_values(
                    self.node_metrics.get_recent_metrics()
                )
            ),
            self.node_metrics._analyze_trends(
                self.node_metrics.get_recent_metrics()
            )
        )
        alert_time = time.time() - start_time
        
        # Verify performance
        self.assertLess(alert_time, 0.5)  # Should take less than 0.5 seconds
        
        # Verify alerts
        self.assertGreater(len(service_alerts), 0)
        self.assertGreater(len(node_alerts), 0)

def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

if __name__ == '__main__':
    unittest.main() 