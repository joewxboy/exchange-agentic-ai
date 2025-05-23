import unittest
from datetime import datetime, timedelta
import os
import asyncio
from unittest.mock import patch, MagicMock
from src.ai.node_agent import NodeManagementAgent
from src.exchange.client import ExchangeAPIClient

class TestNodeAgentIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment with API client and node agent."""
        # Initialize API client with test credentials
        cls.client = ExchangeAPIClient(
            base_url=os.getenv("EXCHANGE_URL", "http://localhost:8080"),
            org=os.getenv("EXCHANGE_ORG", "testorg"),
            username=os.getenv("EXCHANGE_USERNAME", "testuser"),
            password=os.getenv("EXCHANGE_PASSWORD", "testpass")
        )
        
        # Initialize node agent
        cls.node_agent = NodeManagementAgent(cls.client)

    def setUp(self):
        """Set up test data and mocks before each test."""
        # Sample node data from API
        self.node_data = {
            "id": "test-node",
            "name": "Test Node",
            "status": "online",
            "lastHeartbeat": datetime.now().isoformat(),
            "status": {
                "resources": {
                    "cpu": 45.5,
                    "memory": 62.3,
                    "disk": 75.8
                },
                "temperature": 65.0,
                "network": {
                    "status": "connected",
                    "latency": 50.0
                }
            },
            "metrics": {
                "cpu_usage": 45.5,
                "memory_usage": 62.3,
                "disk_usage": 75.8,
                "temperature": 65.0,
                "network_latency": 50.0
            }
        }

    @patch('src.exchange.client.ExchangeAPIClient.list_nodes')
    async def test_node_analysis_integration(self, mock_list_nodes):
        """Test integration of node analysis with API."""
        # Mock API response
        mock_list_nodes.return_value = {
            "nodes": {
                "test-node": self.node_data
            }
        }
        
        # Analyze nodes
        analysis = await self.node_agent.analyze()
        
        # Verify analysis results
        self.assertIn('nodes', analysis)
        self.assertIn('recommendations', analysis)
        self.assertIn('alerts', analysis)
        
        # Verify node analysis
        node_analysis = analysis['nodes']['test-node']
        self.assertIn('status', node_analysis)
        self.assertIn('health', node_analysis)
        self.assertIn('metrics', node_analysis)
        self.assertIn('trends', node_analysis)

    @patch('src.exchange.client.ExchangeAPIClient.get_node')
    @patch('src.exchange.client.ExchangeAPIClient.update_node')
    async def test_node_update_integration(self, mock_update_node, mock_get_node):
        """Test integration of node update with API."""
        # Mock API responses
        mock_get_node.return_value = self.node_data
        mock_update_node.return_value = {"status": "success"}
        
        # Create update action
        action = {
            'node_id': 'test-node',
            'action': 'update',
            'update_data': {
                'status': {
                    'resources': {
                        'cpu': 2.0,
                        'memory': 1024.0,
                        'disk': 2048.0
                    }
                }
            }
        }
        
        # Execute update action
        result = await self.node_agent.act(action)
        
        # Verify result
        self.assertTrue(result)
        mock_update_node.assert_called_once()

    @patch('src.exchange.client.ExchangeAPIClient.get_node')
    async def test_node_health_check_integration(self, mock_get_node):
        """Test integration of node health check with API."""
        # Mock API response
        mock_get_node.return_value = self.node_data
        
        # Create health check action
        action = {
            'node_id': 'test-node',
            'action': 'check_health'
        }
        
        # Execute health check action
        result = await self.node_agent.act(action)
        
        # Verify result
        self.assertTrue(result)
        mock_get_node.assert_called_once()
        
        # Verify health history
        health_history = self.node_agent._health_history
        self.assertGreater(len(health_history), 0)
        latest_check = health_history[-1]
        self.assertEqual(latest_check['node_id'], 'test-node')
        self.assertEqual(latest_check['status'], 'online')

    @patch('src.exchange.client.ExchangeAPIClient.get_node')
    @patch('src.exchange.client.ExchangeAPIClient.update_node')
    async def test_node_cleanup_integration(self, mock_update_node, mock_get_node):
        """Test integration of node cleanup with API."""
        # Mock API responses
        mock_get_node.return_value = self.node_data
        mock_update_node.return_value = {"status": "success"}
        
        # Create cleanup action
        action = {
            'node_id': 'test-node',
            'action': 'cleanup'
        }
        
        # Execute cleanup action
        result = await self.node_agent.act(action)
        
        # Verify result
        self.assertTrue(result)
        mock_update_node.assert_called_once()

    @patch('src.exchange.client.ExchangeAPIClient.list_nodes')
    async def test_node_metrics_collection_integration(self, mock_list_nodes):
        """Test integration of node metrics collection with API."""
        # Mock API response
        mock_list_nodes.return_value = {
            "nodes": {
                "test-node": self.node_data
            }
        }
        
        # Analyze nodes to trigger metrics collection
        analysis = await self.node_agent.analyze()
        
        # Verify metrics collection
        node_analysis = analysis['nodes']['test-node']
        metrics = node_analysis['metrics']
        
        self.assertEqual(metrics['cpu_usage'], 45.5)
        self.assertEqual(metrics['memory_usage'], 62.3)
        self.assertEqual(metrics['disk_usage'], 75.8)
        self.assertEqual(metrics['temperature'], 65.0)
        self.assertEqual(metrics['network_latency'], 50.0)

    @patch('src.exchange.client.ExchangeAPIClient.list_nodes')
    async def test_node_alert_generation_integration(self, mock_list_nodes):
        """Test integration of node alert generation with API."""
        # Create node data with critical metrics
        critical_node_data = self.node_data.copy()
        critical_node_data['metrics'] = {
            'cpu_usage': 95.0,
            'memory_usage': 98.0,
            'disk_usage': 95.0,
            'temperature': 85.0,
            'network_latency': 500.0
        }
        
        # Mock API response
        mock_list_nodes.return_value = {
            "nodes": {
                "test-node": critical_node_data
            }
        }
        
        # Analyze nodes to trigger alert generation
        analysis = await self.node_agent.analyze()
        
        # Verify alerts
        self.assertGreater(len(analysis['alerts']), 0)
        
        # Verify recommendations
        self.assertGreater(len(analysis['recommendations']), 0)
        recommendation = analysis['recommendations'][0]
        self.assertEqual(recommendation['node_id'], 'test-node')
        self.assertIn(recommendation['action'], ['check_health', 'update', 'cleanup'])

    @patch('src.exchange.client.ExchangeAPIClient.list_nodes')
    async def test_node_error_handling_integration(self, mock_list_nodes):
        """Test integration of node error handling with API."""
        # Mock API error response
        mock_list_nodes.side_effect = Exception("API Error")
        
        # Analyze nodes
        analysis = await self.node_agent.analyze()
        
        # Verify error handling
        self.assertEqual(analysis['nodes'], {})
        self.assertEqual(analysis['recommendations'], [])
        self.assertEqual(analysis['alerts'], [])

    @patch('src.exchange.client.ExchangeAPIClient.list_nodes')
    async def test_node_temperature_monitoring_integration(self, mock_list_nodes):
        """Test integration of node temperature monitoring with API."""
        # Create node data with high temperature
        high_temp_node_data = self.node_data.copy()
        high_temp_node_data['metrics']['temperature'] = 85.0
        
        # Mock API response
        mock_list_nodes.return_value = {
            "nodes": {
                "test-node": high_temp_node_data
            }
        }
        
        # Analyze nodes
        analysis = await self.node_agent.analyze()
        
        # Verify temperature monitoring
        node_analysis = analysis['nodes']['test-node']
        self.assertIn('temperature', node_analysis['metrics'])
        self.assertEqual(node_analysis['metrics']['temperature'], 85.0)
        
        # Verify temperature-related alerts
        temp_alerts = [alert for alert in analysis['alerts'] 
                      if 'temperature' in alert.get('reason', '').lower()]
        self.assertGreater(len(temp_alerts), 0)

    @patch('src.exchange.client.ExchangeAPIClient.list_nodes')
    async def test_node_network_monitoring_integration(self, mock_list_nodes):
        """Test integration of node network monitoring with API."""
        # Create node data with network issues
        network_issue_node_data = self.node_data.copy()
        network_issue_node_data['metrics']['network_latency'] = 500.0
        network_issue_node_data['status']['network']['status'] = 'degraded'
        
        # Mock API response
        mock_list_nodes.return_value = {
            "nodes": {
                "test-node": network_issue_node_data
            }
        }
        
        # Analyze nodes
        analysis = await self.node_agent.analyze()
        
        # Verify network monitoring
        node_analysis = analysis['nodes']['test-node']
        self.assertIn('network_latency', node_analysis['metrics'])
        self.assertEqual(node_analysis['metrics']['network_latency'], 500.0)
        
        # Verify network-related alerts
        network_alerts = [alert for alert in analysis['alerts'] 
                         if 'network' in alert.get('reason', '').lower()]
        self.assertGreater(len(network_alerts), 0)

def run_async_test(coro):
    """Helper function to run async tests."""
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)

if __name__ == '__main__':
    unittest.main() 