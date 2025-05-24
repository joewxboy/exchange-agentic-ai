"""
Tests for the ServiceManagementAgent class.
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from src.ai.service_agent import ServiceManagementAgent

@pytest.fixture
def mock_client():
    """Create a mock ExchangeAPIClient."""
    client = MagicMock()
    client.org_id = 'test-org'
    return client

@pytest.fixture
def service_agent(mock_client):
    """Create a ServiceManagementAgent instance for testing."""
    return ServiceManagementAgent(mock_client)

def test_init(service_agent, mock_client):
    """Test initialization of ServiceManagementAgent."""
    assert service_agent.client == mock_client
    assert service_agent._deployment_history == []
    assert isinstance(service_agent.metrics_collector, ServiceManagementAgent.metrics_collector.__class__)

@pytest.mark.asyncio
async def test_analyze_no_services(service_agent, mock_client):
    """Test analyze with no services."""
    mock_client.get_services.return_value = None
    
    analysis = await service_agent.analyze()
    
    assert analysis['services'] == {}
    assert analysis['recommendations'] == []
    assert analysis['alerts'] == []

@pytest.mark.asyncio
async def test_analyze_with_services(service_agent, mock_client):
    """Test analyze with services."""
    # Mock service data
    mock_client.get_services.return_value = [
        {'id': 'service1'},
        {'id': 'service2'}
    ]
    
    mock_client.get_service.side_effect = [
        {'url': 'http://service1.com'},
        {'url': 'http://service2.com'}
    ]
    
    # Mock metrics collector
    with patch.object(service_agent.metrics_collector, 'collect_metrics') as mock_collect, \
         patch.object(service_agent.metrics_collector, 'analyze_metrics') as mock_analyze:
        
        mock_collect.return_value = {
            'cpu_usage': 50.0,
            'memory_usage': 60.0,
            'response_time': 100.0,
            'error_rate': 0.1
        }
        
        mock_analyze.return_value = {
            'status': 'warning',
            'health': 'good',
            'alerts': ['High CPU usage'],
            'recommendations': ['Consider scaling up CPU resources'],
            'metrics': {
                'cpu_usage': 50.0,
                'memory_usage': 60.0,
                'response_time': 100.0,
                'error_rate': 0.1
            }
        }
        
        analysis = await service_agent.analyze()
        
        assert len(analysis['services']) == 2
        assert len(analysis['recommendations']) == 2
        assert len(analysis['alerts']) == 2

def test_determine_action(service_agent):
    """Test determining action from recommendation."""
    assert service_agent._determine_action('Consider scaling up CPU resources') == 'scale'
    assert service_agent._determine_action('Update service configuration') == 'update'
    assert service_agent._determine_action('Restart the service') == 'restart'
    assert service_agent._determine_action('Investigate performance issues') == 'investigate'

@pytest.mark.asyncio
async def test_act_invalid_action(service_agent):
    """Test acting with invalid action."""
    result = await service_agent.act({})
    assert result is False

@pytest.mark.asyncio
async def test_act_scale(service_agent, mock_client):
    """Test scaling a service."""
    # Mock service data
    mock_client.get_service.return_value = {
        'deployment': {
            'resources': {
                'cpu': 1.0,
                'memory': 512.0
            }
        }
    }
    
    # Mock update service
    mock_client.update_service.return_value = {'status': 'success'}
    
    action = {
        'service_id': 'test-service',
        'action': 'scale',
        'scale_factor': 2.0
    }
    
    result = await service_agent.act(action)
    assert result is True
    
    # Verify update was called with correct data
    mock_client.update_service.assert_called_once()
    update_data = mock_client.update_service.call_args[0][2]
    assert update_data['deployment']['resources']['cpu'] == 2.0
    assert update_data['deployment']['resources']['memory'] == 1024.0

@pytest.mark.asyncio
async def test_act_update(service_agent, mock_client):
    """Test updating a service."""
    # Mock update service
    mock_client.update_service.return_value = {'status': 'success'}
    
    action = {
        'service_id': 'test-service',
        'action': 'update',
        'update_data': {'config': 'new-value'}
    }
    
    result = await service_agent.act(action)
    assert result is True
    
    # Verify update was called with correct data
    mock_client.update_service.assert_called_once_with(
        'test-org',
        'test-service',
        {'config': 'new-value'}
    )

@pytest.mark.asyncio
async def test_act_restart(service_agent, mock_client):
    """Test restarting a service."""
    # Mock service data
    mock_client.get_service.return_value = {'config': 'value'}
    
    # Mock update service
    mock_client.update_service.return_value = {'status': 'success'}
    
    action = {
        'service_id': 'test-service',
        'action': 'restart'
    }
    
    result = await service_agent.act(action)
    assert result is True
    
    # Verify update was called with same configuration
    mock_client.update_service.assert_called_once_with(
        'test-org',
        'test-service',
        {'config': 'value'}
    )

@pytest.mark.asyncio
async def test_act_error(service_agent, mock_client):
    """Test acting with error."""
    mock_client.update_service.side_effect = Exception('Update failed')
    
    action = {
        'service_id': 'test-service',
        'action': 'update',
        'update_data': {'config': 'value'}
    }
    
    result = await service_agent.act(action)
    assert result is False 