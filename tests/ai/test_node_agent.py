"""
Unit tests for the node management agent implementation.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.ai.node_agent import NodeManagementAgent

class TestNodeManagementAgent:
    """Test cases for NodeManagementAgent."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock ExchangeAPIClient."""
        client = Mock()
        client.credential_manager._credentials.org_id = "test_org"
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