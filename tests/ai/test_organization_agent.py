"""
Tests for the Organization AI Agent.
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from src.ai.organization_agent import OrganizationAgent
from src.organizations import OrganizationInfo, User
from src.exchange_client import ExchangeAPIClient

@pytest.fixture
def mock_client():
    """Create a mock ExchangeAPIClient."""
    return Mock(spec=ExchangeAPIClient)

@pytest.fixture
def mock_org_manager():
    """Create a mock OrganizationManager."""
    manager = Mock()
    manager.get_organizations = AsyncMock()
    manager.get_users = AsyncMock()
    manager.check_organization_health = AsyncMock()
    manager.update_organization = AsyncMock()
    manager.create_user = AsyncMock()
    manager.update_user = AsyncMock()
    manager.delete_user = AsyncMock()
    return manager

@pytest.fixture
def organization_agent(mock_client, mock_org_manager):
    """Create an OrganizationAgent instance with mocked dependencies."""
    return OrganizationAgent(mock_client, mock_org_manager)

@pytest.fixture
def sample_organization():
    """Create a sample organization for testing."""
    return OrganizationInfo(
        org_id="test-org",
        name="Test Organization",
        description="A test organization",
        created="2024-01-01T00:00:00Z",
        last_updated="2024-01-01T00:00:00Z"
    )

@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        username="testuser",
        org_id="test-org",
        roles=["user"],
        created="2024-01-01T00:00:00Z",
        last_updated="2024-01-01T00:00:00Z"
    )

@pytest.mark.asyncio
async def test_analyze_organizations(organization_agent, mock_org_manager, sample_organization, sample_user):
    """Test organization analysis functionality."""
    # Setup mock responses
    mock_org_manager.get_organizations.return_value = [sample_organization]
    mock_org_manager.get_users.return_value = [sample_user]
    mock_org_manager.check_organization_health.return_value = {
        'status': 'healthy',
        'message': 'All systems operational'
    }
    
    # Perform analysis
    result = await organization_agent.analyze()
    
    # Verify results
    assert result['timestamp'] is not None
    assert len(result['organizations']) == 1
    assert result['organizations'][0]['org_id'] == sample_organization.org_id
    assert result['organizations'][0]['name'] == sample_organization.name
    assert 'health' in result['organizations'][0]
    assert 'user_distribution' in result['organizations'][0]
    
    # Verify mock calls
    mock_org_manager.get_organizations.assert_called_once()
    mock_org_manager.get_users.assert_called_once_with(sample_organization.org_id)
    mock_org_manager.check_organization_health.assert_called_once_with(sample_organization.org_id)

@pytest.mark.asyncio
async def test_analyze_organizations_error(organization_agent, mock_org_manager):
    """Test organization analysis error handling."""
    # Setup mock to raise an exception
    mock_org_manager.get_organizations.side_effect = Exception("Test error")
    
    # Perform analysis
    result = await organization_agent.analyze()
    
    # Verify error handling
    assert result['error'] == "Test error"
    assert len(result['organizations']) == 0
    assert len(result['alerts']) == 1
    assert result['alerts'][0]['type'] == 'error'

@pytest.mark.asyncio
async def test_act_update_organization(organization_agent, mock_org_manager):
    """Test organization update action."""
    action = {
        'type': 'update_organization',
        'org_id': 'test-org',
        'description': 'Updated description'
    }
    
    # Perform action
    result = await organization_agent.act(action)
    
    # Verify results
    assert result is True
    mock_org_manager.update_organization.assert_called_once_with(
        'test-org',
        'Updated description'
    )

@pytest.mark.asyncio
async def test_act_manage_users(organization_agent, mock_org_manager):
    """Test user management action."""
    action = {
        'type': 'manage_users',
        'org_id': 'test-org',
        'subtype': 'create',
        'username': 'newuser',
        'roles': ['user']
    }
    
    # Perform action
    result = await organization_agent.act(action)
    
    # Verify results
    assert result is True
    mock_org_manager.create_user.assert_called_once_with(
        'test-org',
        'newuser',
        ['user']
    )

@pytest.mark.asyncio
async def test_act_health_check(organization_agent, mock_org_manager):
    """Test health check action."""
    action = {
        'type': 'health_check',
        'org_id': 'test-org'
    }
    
    mock_org_manager.check_organization_health.return_value = {
        'status': 'healthy',
        'message': 'All systems operational'
    }
    
    # Perform action
    result = await organization_agent.act(action)
    
    # Verify results
    assert result is True
    mock_org_manager.check_organization_health.assert_called_once_with('test-org')
    
    # Verify state update
    state = organization_agent.get_state()
    assert 'last_health_check' in state
    assert state['last_health_check']['org_id'] == 'test-org'
    assert state['last_health_check']['status'] == 'healthy'

@pytest.mark.asyncio
async def test_act_invalid_action(organization_agent):
    """Test invalid action handling."""
    action = {
        'type': 'invalid_action',
        'org_id': 'test-org'
    }
    
    # Perform action
    result = await organization_agent.act(action)
    
    # Verify results
    assert result is False

def test_process_experience(organization_agent):
    """Test experience processing."""
    experience = {
        'organization_changes': True,
        'user_changes': True
    }
    
    # Process experience
    organization_agent._process_experience(experience)
    
    # Verify cache clearing
    assert len(organization_agent._org_cache) == 0
    assert len(organization_agent._user_cache) == 0

def test_get_metrics(organization_agent):
    """Test metrics collection."""
    # Add some test data
    organization_agent._org_cache['test-org'] = Mock()
    organization_agent._user_cache['test-org'] = {'testuser': Mock()}
    organization_agent.update_state({
        'last_health_check': {
            'timestamp': '2024-01-01T00:00:00Z'
        }
    })
    
    # Get metrics
    metrics = organization_agent.get_metrics()
    
    # Verify metrics
    assert metrics['cached_orgs'] == 1
    assert metrics['cached_users'] == 1
    assert metrics['last_health_check'] == '2024-01-01T00:00:00Z' 