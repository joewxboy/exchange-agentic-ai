import unittest
from datetime import datetime, timedelta
import os
import asyncio
from unittest.mock import patch, MagicMock
from src.ai.service_agent import ServiceManagementAgent
from src.exchange.client import ExchangeAPIClient

class TestServiceAgentIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment with API client and service agent."""
        # Initialize API client with test credentials
        cls.client = ExchangeAPIClient(
            base_url=os.getenv("EXCHANGE_URL", "http://localhost:8080"),
            org=os.getenv("EXCHANGE_ORG", "testorg"),
            username=os.getenv("EXCHANGE_USERNAME", "testuser"),
            password=os.getenv("EXCHANGE_PASSWORD", "testpass")
        )
        
        # Initialize service agent
        cls.service_agent = ServiceManagementAgent(cls.client)

    def setUp(self):
        """Set up test data and mocks before each test."""
        # Sample service data from API
        self.service_data = {
            "id": "test-service",
            "name": "Test Service",
            "version": "1.0.0",
            "status": "running",
            "deployment": {
                "resources": {
                    "cpu": 1.0,
                    "memory": 512.0
                }
            },
            "metrics": {
                "cpu_usage": 65.5,
                "memory_usage": 72.3,
                "error_rate": 0.03,
                "response_time": 250.0
            }
        }

    @patch('src.exchange.client.ExchangeAPIClient.list_services')
    async def test_service_analysis_integration(self, mock_list_services):
        """Test integration of service analysis with API."""
        # Mock API response
        mock_list_services.return_value = {
            "services": {
                "test-service": self.service_data
            }
        }
        
        # Analyze services
        analysis = await self.service_agent.analyze()
        
        # Verify analysis results
        self.assertIn('services', analysis)
        self.assertIn('recommendations', analysis)
        self.assertIn('alerts', analysis)
        
        # Verify service analysis
        service_analysis = analysis['services']['test-service']
        self.assertIn('status', service_analysis)
        self.assertIn('health', service_analysis)
        self.assertIn('metrics', service_analysis)
        self.assertIn('trends', service_analysis)

    @patch('src.exchange.client.ExchangeAPIClient.get_service')
    @patch('src.exchange.client.ExchangeAPIClient.update_service')
    async def test_service_update_integration(self, mock_update_service, mock_get_service):
        """Test integration of service update with API."""
        # Mock API responses
        mock_get_service.return_value = self.service_data
        mock_update_service.return_value = {"status": "success"}
        
        # Create update action
        action = {
            'service_id': 'test-service',
            'action': 'update',
            'update_data': {
                'deployment': {
                    'resources': {
                        'cpu': 2.0,
                        'memory': 1024.0
                    }
                }
            }
        }
        
        # Execute update action
        result = await self.service_agent.act(action)
        
        # Verify result
        self.assertTrue(result)
        mock_update_service.assert_called_once()

    @patch('src.exchange.client.ExchangeAPIClient.get_service')
    @patch('src.exchange.client.ExchangeAPIClient.update_service')
    async def test_service_scale_integration(self, mock_update_service, mock_get_service):
        """Test integration of service scaling with API."""
        # Mock API responses
        mock_get_service.return_value = self.service_data
        mock_update_service.return_value = {"status": "success"}
        
        # Create scale action
        action = {
            'service_id': 'test-service',
            'action': 'scale',
            'scale_factor': 2.0
        }
        
        # Execute scale action
        result = await self.service_agent.act(action)
        
        # Verify result
        self.assertTrue(result)
        mock_update_service.assert_called_once()
        
        # Verify scaled resources
        update_data = mock_update_service.call_args[0][2]
        self.assertEqual(update_data['deployment']['resources']['cpu'], 2.0)
        self.assertEqual(update_data['deployment']['resources']['memory'], 1024.0)

    @patch('src.exchange.client.ExchangeAPIClient.get_service')
    @patch('src.exchange.client.ExchangeAPIClient.update_service')
    async def test_service_restart_integration(self, mock_update_service, mock_get_service):
        """Test integration of service restart with API."""
        # Mock API responses
        mock_get_service.return_value = self.service_data
        mock_update_service.return_value = {"status": "success"}
        
        # Create restart action
        action = {
            'service_id': 'test-service',
            'action': 'restart'
        }
        
        # Execute restart action
        result = await self.service_agent.act(action)
        
        # Verify result
        self.assertTrue(result)
        mock_update_service.assert_called_once()
        
        # Verify same configuration was used
        update_data = mock_update_service.call_args[0][2]
        self.assertEqual(update_data, self.service_data)

    @patch('src.exchange.client.ExchangeAPIClient.list_services')
    async def test_service_metrics_collection_integration(self, mock_list_services):
        """Test integration of service metrics collection with API."""
        # Mock API response
        mock_list_services.return_value = {
            "services": {
                "test-service": self.service_data
            }
        }
        
        # Analyze services to trigger metrics collection
        analysis = await self.service_agent.analyze()
        
        # Verify metrics collection
        service_analysis = analysis['services']['test-service']
        metrics = service_analysis['metrics']
        
        self.assertEqual(metrics['cpu_usage'], 65.5)
        self.assertEqual(metrics['memory_usage'], 72.3)
        self.assertEqual(metrics['error_rate'], 0.03)
        self.assertEqual(metrics['response_time'], 250.0)

    @patch('src.exchange.client.ExchangeAPIClient.list_services')
    async def test_service_alert_generation_integration(self, mock_list_services):
        """Test integration of service alert generation with API."""
        # Create service data with critical metrics
        critical_service_data = self.service_data.copy()
        critical_service_data['metrics'] = {
            'cpu_usage': 95.0,
            'memory_usage': 98.0,
            'error_rate': 0.15,
            'response_time': 2000.0
        }
        
        # Mock API response
        mock_list_services.return_value = {
            "services": {
                "test-service": critical_service_data
            }
        }
        
        # Analyze services to trigger alert generation
        analysis = await self.service_agent.analyze()
        
        # Verify alerts
        self.assertGreater(len(analysis['alerts']), 0)
        
        # Verify recommendations
        self.assertGreater(len(analysis['recommendations']), 0)
        recommendation = analysis['recommendations'][0]
        self.assertEqual(recommendation['service_id'], 'test-service')
        self.assertIn(recommendation['action'], ['update', 'scale', 'restart'])

    @patch('src.exchange.client.ExchangeAPIClient.list_services')
    async def test_service_error_handling_integration(self, mock_list_services):
        """Test integration of service error handling with API."""
        # Mock API error response
        mock_list_services.side_effect = Exception("API Error")
        
        # Analyze services
        analysis = await self.service_agent.analyze()
        
        # Verify error handling
        self.assertEqual(analysis['services'], {})
        self.assertEqual(analysis['recommendations'], [])
        self.assertEqual(analysis['alerts'], [])

def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

if __name__ == '__main__':
    unittest.main() 