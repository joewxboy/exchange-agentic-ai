"""
Unit tests for the node management agent implementation.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from src.ai.node_agent import NodeManagementAgent

class TestNodeManagementAgent:
    """Test cases for NodeManagementAgent."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock ExchangeAPIClient."""
        client = Mock()
        client.credential_manager._credentials.org_id = "test_org"
        # Patch async methods
        client.get_node = AsyncMock()
        client.create_node = AsyncMock()
        client.delete_node = AsyncMock()
        client.update_node = AsyncMock()
        client.list_nodes = AsyncMock()
        return client
    
    @pytest.fixture
    def agent(self, mock_client):
        """Create a test instance of NodeManagementAgent."""
        return NodeManagementAgent(mock_client)
    
    @pytest.mark.asyncio
    async def test_analyze_no_nodes(self, agent, mock_client):
        """Test analysis with no nodes."""
        mock_client.list_nodes.return_value = {'nodes': {}}
        analysis = await agent.analyze()
        assert analysis['nodes'] == {}
        assert analysis['recommendations'] == []
        assert analysis['alerts'] == []
    
    @pytest.mark.asyncio
    async def test_analyze_nodes(self, agent, mock_client):
        """Test analysis with nodes."""
        mock_client.list_nodes.return_value = {
            'nodes': {
                'node1': {'status': 'online'},
                'node2': {'status': 'online'}
            }
        }
        
        analysis = await agent.analyze()
        assert len(analysis['nodes']) == 2
        assert 'node1' in analysis['nodes']
        assert 'node2' in analysis['nodes']
    
    @pytest.mark.asyncio
    async def test_analyze_node_error(self, agent, mock_client):
        """Test analysis with node error."""
        mock_client.list_nodes.return_value = {
            'nodes': {
                'node1': {'status': 'online'}
            }
        }
        
        # Create a mock for the metrics collector
        mock_collector = Mock()
        mock_collector.collect_metrics.side_effect = Exception("Test error")
        agent._metrics_collector = mock_collector
        
        analysis = await agent.analyze()
        assert len(analysis['alerts']) == 1
        assert analysis['alerts'][0]['type'] == 'error'
    
    @pytest.mark.asyncio
    async def test_act_check_health(self, agent, mock_client):
        """Test check health action."""
        mock_client.get_node.return_value = {
            'status': 'online',
            'lastHeartbeat': '2024-03-20T12:00:00Z'
        }
        
        action = {
            'node_id': 'node1',
            'action': 'check_health'
        }
        
        result = await agent.act(action)
        assert result is True
        assert len(agent._health_history) == 1
    
    @pytest.mark.asyncio
    async def test_act_update(self, agent, mock_client):
        """Test update action."""
        action = {
            'node_id': 'node1',
            'action': 'update',
            'update_data': {'config': 'new_value'}
        }
        
        result = await agent.act(action)
        assert result is True
        assert len(agent._history) == 1
    
    @pytest.mark.asyncio
    async def test_act_cleanup(self, agent, mock_client):
        """Test cleanup action."""
        mock_client.get_node.return_value = {
            'status': {
                'resources': {
                    'disk': 85.0
                }
            }
        }
        
        action = {
            'node_id': 'node1',
            'action': 'cleanup'
        }
        
        result = await agent.act(action)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_act_invalid(self, agent):
        """Test invalid action."""
        action = {
            'node_id': 'node1',
            'action': 'invalid'
        }
        
        result = await agent.act(action)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_act_missing_data(self, agent):
        """Test action with missing data."""
        action = {
            'action': 'check_health'  # Missing node_id
        }
        
        result = await agent.act(action)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_node_health(self, agent, mock_client):
        """Test node health check."""
        mock_client.get_node.return_value = {
            'status': 'online',
            'lastHeartbeat': '2024-03-20T12:00:00Z'
        }
        
        result = await agent._check_node_health('node1')
        assert result is True
        assert len(agent._health_history) == 1
    
    @pytest.mark.asyncio
    async def test_check_node_health_error(self, agent, mock_client):
        """Test node health check with error."""
        mock_client.get_node.side_effect = Exception("Test error")
        result = await agent._check_node_health('node1')
        assert result is False
    
    @pytest.mark.asyncio
    async def test_update_node(self, agent, mock_client):
        """Test node update."""
        update_data = {'config': 'new_value'}
        result = await agent._update_node('node1', update_data)
        assert result is True
        assert len(agent._history) == 1
    
    @pytest.mark.asyncio
    async def test_update_node_error(self, agent, mock_client):
        """Test node update with error."""
        mock_client.update_node.side_effect = Exception("Test error")
        result = await agent._update_node('node1', {})
        assert result is False
    
    @pytest.mark.asyncio
    async def test_cleanup_node(self, agent, mock_client):
        """Test node cleanup."""
        mock_client.get_node.return_value = {
            'status': {
                'resources': {
                    'disk': 85.0
                }
            }
        }
        
        result = await agent._cleanup_node('node1')
        assert result is True
    
    @pytest.mark.asyncio
    async def test_cleanup_node_error(self, agent, mock_client):
        """Test node cleanup with error."""
        mock_client.get_node.side_effect = Exception("Test error")
        result = await agent._cleanup_node('node1')
        assert result is False
    
    @pytest.mark.asyncio
    async def test_register_node_success(self, agent, mock_client):
        """Test successful node registration."""
        node_data = {
            'name': 'test-node',
            'nodeType': 'device',
            'publicKey': 'test-key',
            'token': 'test-token',
            'registeredServices': ['service1'],
            'policy': {'constraints': []}
        }
        
        mock_client.create_node.return_value = {
            'status': 'success',
            'node_id': 'test-node-id'
        }
        
        result = await agent.register_node(node_data)
        assert result['status'] == 'success'
        assert result['node_id'] == 'test-node-id'
        assert 'message' in result
    
    @pytest.mark.asyncio
    async def test_register_node_validation(self, agent):
        """Test node registration with invalid data."""
        # Test missing required fields
        invalid_data = {
            'name': 'test-node'
            # Missing required fields
        }
        
        result = await agent.register_node(invalid_data)
        assert result['status'] == 'error'
        assert 'validation' in result['message'].lower()
        
        # Test invalid field types
        invalid_types = {
            'name': 123,  # Should be string
            'nodeType': 'device',
            'publicKey': 'test-key',
            'token': 'test-token',
            'registeredServices': 'not-a-list',  # Should be list
            'policy': {'constraints': []}
        }
        
        result = await agent.register_node(invalid_types)
        assert result['status'] == 'error'
        assert 'validation' in result['message'].lower()
    
    @pytest.mark.asyncio
    async def test_register_node_duplicate(self, agent, mock_client):
        """Test node registration with duplicate name."""
        node_data = {
            'name': 'existing-node',
            'nodeType': 'device',
            'publicKey': 'test-key',
            'token': 'test-token',
            'registeredServices': ['service1'],
            'policy': {'constraints': []}
        }
        
        mock_client.create_node.side_effect = Exception("Node already exists")
        
        result = await agent.register_node(node_data)
        assert result['status'] == 'error'
        assert 'already exists' in result['message'].lower()
    
    @pytest.mark.asyncio
    async def test_register_node_api_error(self, agent, mock_client):
        """Test node registration with API error."""
        node_data = {
            'name': 'test-node',
            'nodeType': 'device',
            'publicKey': 'test-key',
            'token': 'test-token',
            'registeredServices': ['service1'],
            'policy': {'constraints': []}
        }
        
        mock_client.create_node.side_effect = Exception("API Error")
        
        result = await agent.register_node(node_data)
        assert result['status'] == 'error'
        assert 'api' in result['message'].lower()
    
    @pytest.mark.asyncio
    async def test_register_node_edge_cases(self, agent, mock_client):
        """Test node registration edge cases."""
        # Test empty service list
        empty_services = {
            'name': 'test-node',
            'nodeType': 'device',
            'publicKey': 'test-key',
            'token': 'test-token',
            'registeredServices': [],
            'policy': {'constraints': []}
        }
        
        mock_client.create_node.return_value = {
            'status': 'success',
            'node_id': 'test-node-id'
        }
        
        result = await agent.register_node(empty_services)
        assert result['status'] == 'success'
        
        # Test minimal policy
        minimal_policy = {
            'name': 'test-node',
            'nodeType': 'device',
            'publicKey': 'test-key',
            'token': 'test-token',
            'registeredServices': ['service1'],
            'policy': {}
        }
        
        result = await agent.register_node(minimal_policy)
        assert result['status'] == 'success'

    @pytest.mark.asyncio
    async def test_delete_node_success(self, agent, mock_client):
        """Test successful node deletion."""
        mock_client.delete_node.return_value = {'status': 'success', 'message': 'Node deleted'}
        result = await agent.delete_node('test-node-id')
        assert result['status'] == 'success'
        assert 'message' in result

    @pytest.mark.asyncio
    async def test_delete_node_not_found(self, agent, mock_client):
        """Test deletion of a non-existent node."""
        mock_client.delete_node.side_effect = Exception("Node not found")
        result = await agent.delete_node('nonexistent-node')
        assert result['status'] == 'error'
        assert 'not found' in result['message'].lower()

    @pytest.mark.asyncio
    async def test_delete_node_invalid_id(self, agent):
        """Test deletion with invalid node_id (missing or not a string)."""
        # Missing node_id (None)
        result = await agent.delete_node(None)
        assert result['status'] == 'error'
        assert 'node_id' in result['message'].lower()
        # Not a string
        result = await agent.delete_node(123)
        assert result['status'] == 'error'
        assert 'node_id' in result['message'].lower()

    @pytest.mark.asyncio
    async def test_delete_node_api_error(self, agent, mock_client):
        """Test API error during node deletion."""
        mock_client.delete_node.side_effect = Exception("API Error: Internal server error")
        result = await agent.delete_node('test-node-id')
        assert result['status'] == 'error'
        assert 'api' in result['message'].lower()

    @pytest.mark.asyncio
    async def test_delete_node_edge_cases(self, agent, mock_client):
        """Test edge cases for node deletion (e.g., node with dependencies)."""
        # Simulate dependency error
        mock_client.delete_node.side_effect = Exception("Cannot delete node: dependencies exist")
        result = await agent.delete_node('dependent-node')
        assert result['status'] == 'error'
        assert 'dependencies' in result['message'].lower()

    @pytest.mark.asyncio
    async def test_get_node_status_success(self, agent, mock_client):
        """Test successful node status retrieval."""
        mock_client.get_node.return_value = {
            'status': 'online',
            'health': 'good',
            'metrics': {'cpu': 50, 'memory': 60},
            'trends': {'cpu': 'stable', 'memory': 'stable'}
        }
        result = await agent.get_node_status('test-node-id')
        assert result['status'] == 'online'
        assert result['health'] == 'good'
        assert 'metrics' in result
        assert 'trends' in result

    @pytest.mark.asyncio
    async def test_get_node_status_not_found(self, agent, mock_client):
        """Test status retrieval for a non-existent node."""
        mock_client.get_node.side_effect = Exception("Node not found")
        result = await agent.get_node_status('nonexistent-node')
        assert result['status'] == 'error'
        assert 'not found' in result['message'].lower()

    @pytest.mark.asyncio
    async def test_get_node_status_invalid_id(self, agent):
        """Test status retrieval with invalid node_id (missing or not a string)."""
        # Missing node_id (None)
        result = await agent.get_node_status(None)
        assert result['status'] == 'error'
        assert 'node_id' in result['message'].lower()
        # Not a string
        result = await agent.get_node_status(123)
        assert result['status'] == 'error'
        assert 'node_id' in result['message'].lower()

    @pytest.mark.asyncio
    async def test_get_node_status_api_error(self, agent, mock_client):
        """Test API error during node status retrieval."""
        mock_client.get_node.side_effect = Exception("API Error: Internal server error")
        result = await agent.get_node_status('test-node-id')
        assert result['status'] == 'error'
        assert 'api' in result['message'].lower()

    @pytest.mark.asyncio
    async def test_get_node_status_edge_cases(self, agent, mock_client):
        """Test edge cases for node status retrieval (e.g., minimal or unusual status data)."""
        # Simulate minimal status data
        mock_client.get_node.return_value = {
            'status': 'online',
            'health': 'unknown',
            'metrics': {},
            'trends': {}
        }
        result = await agent.get_node_status('minimal-node')
        assert result['status'] == 'online'
        assert result['health'] == 'unknown'
        assert 'metrics' in result
        assert 'trends' in result 