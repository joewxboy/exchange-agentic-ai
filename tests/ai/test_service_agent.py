"""
Unit tests for the service management agent implementation.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.ai.service_agent import ServiceManagementAgent

class TestServiceManagementAgent:
    """Test cases for ServiceManagementAgent."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock ExchangeAPIClient."""
        client = Mock()
        client.org_id = "test_org"
        return client
    
    @pytest.fixture
    def agent(self, mock_client):
        """Create a test instance of ServiceManagementAgent."""
        return ServiceManagementAgent(mock_client)
    
    @pytest.mark.asyncio
    async def test_analyze_no_services(self, agent, mock_client):
        """Test analysis with no services."""
        mock_client.get_services.return_value = []
        analysis = await agent.analyze()
        assert analysis['services'] == {}
        assert analysis['recommendations'] == []
        assert analysis['alerts'] == []
    
    @pytest.mark.asyncio
    async def test_analyze_services(self, agent, mock_client):
        """Test analysis with services."""
        mock_client.get_services.return_value = [
            {'id': 'service1', 'name': 'Test Service 1'},
            {'id': 'service2', 'name': 'Test Service 2'}
        ]
        
        mock_client.get_service.side_effect = [
            {'id': 'service1', 'status': 'running'},
            {'id': 'service2', 'status': 'running'}
        ]
        
        analysis = await agent.analyze()
        assert len(analysis['services']) == 2
        assert 'service1' in analysis['services']
        assert 'service2' in analysis['services']
    
    @pytest.mark.asyncio
    async def test_analyze_service_error(self, agent, mock_client):
        """Test analysis with service error."""
        mock_client.get_services.return_value = [
            {'id': 'service1', 'name': 'Test Service 1'}
        ]
        mock_client.get_service.side_effect = Exception("Test error")
        
        analysis = await agent.analyze()
        assert len(analysis['alerts']) == 1
        assert analysis['alerts'][0]['type'] == 'error'
    
    def test_determine_action(self, agent):
        """Test action determination from recommendations."""
        assert agent._determine_action("Scale up CPU resources") == 'scale'
        assert agent._determine_action("Update service configuration") == 'update'
        assert agent._determine_action("Restart service") == 'restart'
        assert agent._determine_action("Check service logs") == 'investigate'
    
    @pytest.mark.asyncio
    async def test_act_scale(self, agent, mock_client):
        """Test scale action."""
        mock_client.get_service.return_value = {
            'deployment': {
                'resources': {
                    'cpu': 1.0,
                    'memory': 512.0
                }
            }
        }
        
        action = {
            'service_id': 'service1',
            'action': 'scale',
            'scale_factor': 2.0
        }
        
        result = await agent.act(action)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_act_update(self, agent, mock_client):
        """Test update action."""
        action = {
            'service_id': 'service1',
            'action': 'update',
            'update_data': {'config': 'new_value'}
        }
        
        result = await agent.act(action)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_act_restart(self, agent, mock_client):
        """Test restart action."""
        mock_client.get_service.return_value = {
            'id': 'service1',
            'config': 'test'
        }
        
        action = {
            'service_id': 'service1',
            'action': 'restart'
        }
        
        result = await agent.act(action)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_act_invalid(self, agent):
        """Test invalid action."""
        action = {
            'service_id': 'service1',
            'action': 'invalid'
        }
        
        result = await agent.act(action)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_act_missing_data(self, agent):
        """Test action with missing data."""
        action = {
            'action': 'scale'  # Missing service_id
        }
        
        result = await agent.act(action)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_update_service(self, agent, mock_client):
        """Test service update."""
        update_data = {'config': 'new_value'}
        result = await agent._update_service('service1', update_data)
        assert result is True
        assert len(agent._deployment_history) == 1
    
    @pytest.mark.asyncio
    async def test_update_service_error(self, agent, mock_client):
        """Test service update with error."""
        mock_client.update_service.side_effect = Exception("Test error")
        result = await agent._update_service('service1', {})
        assert result is False
    
    @pytest.mark.asyncio
    async def test_scale_service(self, agent, mock_client):
        """Test service scaling."""
        mock_client.get_service.return_value = {
            'deployment': {
                'resources': {
                    'cpu': 1.0,
                    'memory': 512.0
                }
            }
        }
        
        result = await agent._scale_service('service1', 2.0)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_scale_service_error(self, agent, mock_client):
        """Test service scaling with error."""
        mock_client.get_service.side_effect = Exception("Test error")
        result = await agent._scale_service('service1', 2.0)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_restart_service(self, agent, mock_client):
        """Test service restart."""
        mock_client.get_service.return_value = {
            'id': 'service1',
            'config': 'test'
        }
        
        result = await agent._restart_service('service1')
        assert result is True
    
    @pytest.mark.asyncio
    async def test_restart_service_error(self, agent, mock_client):
        """Test service restart with error."""
        mock_client.get_service.side_effect = Exception("Test error")
        result = await agent._restart_service('service1')
        assert result is False 