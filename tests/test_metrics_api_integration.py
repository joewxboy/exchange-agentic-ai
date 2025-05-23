import unittest
from datetime import datetime, timedelta
import os
import asyncio
import json
from unittest.mock import patch, MagicMock
from src.ai.metrics import MetricsCollector
from src.ai.service_metrics import ServiceMetricsCollector
from src.ai.node_metrics import NodeMetricsCollector
from src.exchange.client import ExchangeAPIClient

class TestMetricsAPIIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment with API client and metrics collectors."""
        # Initialize API client with test credentials
        cls.client = ExchangeAPIClient(
            base_url=os.getenv("EXCHANGE_URL", "http://localhost:8080"),
            org=os.getenv("EXCHANGE_ORG", "testorg"),
            username=os.getenv("EXCHANGE_USERNAME", "testuser"),
            password=os.getenv("EXCHANGE_PASSWORD", "testpass")
        )
        
        # Initialize metrics collectors
        cls.service_metrics = ServiceMetricsCollector()
        cls.node_metrics = NodeMetricsCollector()

    def setUp(self):
        """Set up test data and mocks before each test."""
        # Sample service data from API
        self.service_data = {
            "id": "test-service",
            "name": "Test Service",
            "version": "1.0.0",
            "status": "running",
            "metrics": {
                "cpu_usage": 65.5,
                "memory_usage": 72.3,
                "error_rate": 0.03,
                "response_time": 250.0
            }
        }
        
        # Sample node data from API
        self.node_data = {
            "id": "test-node",
            "name": "Test Node",
            "status": "online",
            "metrics": {
                "cpu_usage": 45.5,
                "memory_usage": 62.3,
                "disk_usage": 75.8,
                "temperature": 65.0
            }
        }

    @patch('src.exchange.client.ExchangeAPIClient.get')
    async def test_service_metrics_api_integration(self, mock_get):
        """Test integration between service metrics collector and API."""
        # Mock API response
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"services": [self.service_data]}
        )
        
        # Get service data from API
        response = await self.client.get("/services")
        services = response.json()["services"]
        
        # Add metrics to collector
        for service in services:
            metrics = service["metrics"]
            metrics["timestamp"] = datetime.now()
            self.service_metrics.add_metrics(metrics)
        
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
        
        # Verify metrics match API data
        self.assertEqual(recent_metrics[0]["cpu_usage"], self.service_data["metrics"]["cpu_usage"])
        self.assertEqual(recent_metrics[0]["memory_usage"], self.service_data["metrics"]["memory_usage"])

    @patch('src.exchange.client.ExchangeAPIClient.get')
    async def test_node_metrics_api_integration(self, mock_get):
        """Test integration between node metrics collector and API."""
        # Mock API response
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {"nodes": [self.node_data]}
        )
        
        # Get node data from API
        response = await self.client.get("/nodes")
        nodes = response.json()["nodes"]
        
        # Add metrics to collector
        for node in nodes:
            metrics = node["metrics"]
            metrics["timestamp"] = datetime.now()
            self.node_metrics.add_metrics(metrics)
        
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
        
        # Verify metrics match API data
        self.assertEqual(recent_metrics[0]["cpu_usage"], self.node_data["metrics"]["cpu_usage"])
        self.assertEqual(recent_metrics[0]["memory_usage"], self.node_data["metrics"]["memory_usage"])

    @patch('src.exchange.client.ExchangeAPIClient.get')
    async def test_metrics_api_error_handling(self, mock_get):
        """Test error handling in metrics API integration."""
        # Mock API error response
        mock_get.return_value = MagicMock(
            status_code=500,
            json=lambda: {"error": "Internal Server Error"}
        )
        
        # Attempt to get service data from API
        with self.assertRaises(Exception):
            await self.client.get("/services")
        
        # Verify metrics collector handles missing data
        analysis = self.service_metrics.analyze_metrics([])
        self.assertEqual(analysis["status"], "unknown")
        self.assertEqual(analysis["health"], "unknown")

    @patch('src.exchange.client.ExchangeAPIClient.get')
    async def test_metrics_api_rate_limiting(self, mock_get):
        """Test rate limiting handling in metrics API integration."""
        # Mock API rate limit response
        mock_get.return_value = MagicMock(
            status_code=429,
            json=lambda: {"error": "Rate limit exceeded"}
        )
        
        # Attempt to get service data from API
        with self.assertRaises(Exception):
            await self.client.get("/services")
        
        # Verify metrics collector continues to function with existing data
        self.service_metrics.add_metrics({
            "cpu_usage": 65.5,
            "memory_usage": 72.3,
            "timestamp": datetime.now()
        })
        
        analysis = self.service_metrics.analyze_metrics(
            self.service_metrics.get_recent_metrics()
        )
        self.assertIn('status', analysis)
        self.assertIn('health', analysis)

    @patch('src.exchange.client.ExchangeAPIClient.get')
    async def test_metrics_api_data_consistency(self, mock_get):
        """Test data consistency between API and metrics collector."""
        # Mock API response with multiple services
        mock_get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "services": [
                    self.service_data,
                    {
                        "id": "test-service-2",
                        "name": "Test Service 2",
                        "version": "1.0.0",
                        "status": "running",
                        "metrics": {
                            "cpu_usage": 75.5,
                            "memory_usage": 82.3,
                            "error_rate": 0.05,
                            "response_time": 350.0
                        }
                    }
                ]
            }
        )
        
        # Get service data from API
        response = await self.client.get("/services")
        services = response.json()["services"]
        
        # Add metrics to collector
        for service in services:
            metrics = service["metrics"]
            metrics["timestamp"] = datetime.now()
            self.service_metrics.add_metrics(metrics)
        
        # Get recent metrics
        recent_metrics = self.service_metrics.get_recent_metrics()
        
        # Verify all services are represented in metrics
        self.assertEqual(len(recent_metrics), len(services))
        
        # Verify metrics values match API data
        for i, service in enumerate(services):
            self.assertEqual(recent_metrics[i]["cpu_usage"], service["metrics"]["cpu_usage"])
            self.assertEqual(recent_metrics[i]["memory_usage"], service["metrics"]["memory_usage"])

def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

if __name__ == '__main__':
    unittest.main() 