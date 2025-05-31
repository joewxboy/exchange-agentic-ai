"""
Tests for the User Agent.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from src.ai.user_agent import UserAgent
from src.organizations import User, OrganizationInfo

@pytest.fixture
def mock_client():
    """Create a mock ExchangeAPIClient."""
    client = Mock()
    client.get_user = AsyncMock()
    client.get_organization = AsyncMock()
    return client

@pytest.fixture
def mock_org_manager():
    """Create a mock OrganizationManager."""
    manager = Mock()
    manager.get_organization = AsyncMock()
    manager.get_user = AsyncMock()
    manager.update_user = AsyncMock()
    return manager

@pytest.fixture
def user_agent(mock_client, mock_org_manager):
    """Create a UserAgent instance with mocked dependencies."""
    return UserAgent(mock_client, mock_org_manager)

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

@pytest.mark.asyncio
async def test_analyze_users(user_agent, sample_user, sample_organization):
    """Test user analysis functionality."""
    # Setup mocks
    user_agent.org_manager.get_organization.return_value = sample_organization
    user_agent.org_manager.get_user.return_value = sample_user
    
    # Call analyze
    result = await user_agent.analyze()
    
    # Verify results
    assert result['status'] == 'success'
    assert len(result['analysis']) > 0
    assert len(result['recommendations']) >= 0
    assert len(result['alerts']) >= 0
    
    # Verify mock calls
    user_agent.org_manager.get_organization.assert_called_once()
    user_agent.org_manager.get_user.assert_called()

@pytest.mark.asyncio
async def test_analyze_users_error(user_agent):
    """Test error handling in user analysis."""
    # Setup mock to raise exception
    user_agent.org_manager.get_organization.side_effect = Exception("Test error")
    
    # Call analyze
    result = await user_agent.analyze()
    
    # Verify error handling
    assert result['status'] == 'error'
    assert 'error' in result
    assert 'Test error' in str(result['error'])

@pytest.mark.asyncio
async def test_act_update_user(user_agent, sample_user):
    """Test user update action."""
    # Setup test data
    action = {
        'type': 'update_user',
        'user_id': 'testuser',
        'org_id': 'test-org',
        'updates': {
            'roles': ['admin']
        }
    }
    
    # Setup mocks
    user_agent.org_manager.update_user.return_value = sample_user
    
    # Call act
    result = await user_agent.act(action)
    
    # Verify results
    assert result['status'] == 'success'
    assert result['action'] == 'update_user'
    assert result['user_id'] == 'testuser'
    
    # Verify mock calls
    user_agent.org_manager.update_user.assert_called_once()

@pytest.mark.asyncio
async def test_act_health_check(user_agent, sample_user):
    """Test health check action."""
    # Setup test data
    action = {
        'type': 'health_check',
        'user_id': 'testuser',
        'org_id': 'test-org'
    }
    
    # Setup mocks
    user_agent.org_manager.get_user.return_value = sample_user
    
    # Call act
    result = await user_agent.act(action)
    
    # Verify results
    assert result['status'] == 'success'
    assert result['action'] == 'health_check'
    assert result['user_id'] == 'testuser'
    assert 'health' in result
    
    # Verify mock calls
    user_agent.org_manager.get_user.assert_called_once()

@pytest.mark.asyncio
async def test_act_invalid_action(user_agent):
    """Test handling of invalid actions."""
    # Setup test data
    action = {
        'type': 'invalid_action',
        'user_id': 'testuser',
        'org_id': 'test-org'
    }
    
    # Call act
    result = await user_agent.act(action)
    
    # Verify results
    assert result['status'] == 'error'
    assert 'error' in result
    assert 'Invalid action type' in str(result['error'])

def test_analyze_user(user_agent, sample_user):
    """Test individual user analysis."""
    # Call analyze_user
    analysis = user_agent._analyze_user(sample_user)
    
    # Verify analysis
    assert analysis['status'] == 'success'
    assert 'health' in analysis
    assert 'roles' in analysis
    assert 'activity' in analysis
    assert len(analysis['recommendations']) >= 0
    assert len(analysis['alerts']) >= 0

def test_analyze_user_roles(user_agent, sample_user):
    """Test user role analysis."""
    # Call analyze_user_roles
    roles_analysis = user_agent._analyze_user_roles(sample_user)
    
    # Verify analysis
    assert roles_analysis['status'] == 'success'
    assert 'roles' in roles_analysis
    assert 'is_admin' in roles_analysis
    assert 'is_super_admin' in roles_analysis
    assert len(roles_analysis['recommendations']) >= 0

def test_analyze_user_activity(user_agent, sample_user):
    """Test user activity analysis."""
    # Call analyze_user_activity
    activity_analysis = user_agent._analyze_user_activity(sample_user)
    
    # Verify analysis
    assert activity_analysis['status'] == 'success'
    assert 'inactivity_days' in activity_analysis
    assert 'activity_level' in activity_analysis
    assert len(activity_analysis['recommendations']) >= 0
    assert len(activity_analysis['alerts']) >= 0

def test_process_experience(user_agent, sample_user):
    """Test experience processing."""
    # Setup test data
    experience = {
        'type': 'user_update',
        'user_id': 'testuser',
        'org_id': 'test-org',
        'changes': {
            'roles': ['admin']
        }
    }
    
    # Call process_experience
    user_agent._process_experience(experience)
    
    # Verify state updates
    assert 'testuser' in user_agent.user_cache
    assert user_agent.user_cache['testuser']['roles'] == ['admin']

def test_get_metrics(user_agent):
    """Test metrics collection."""
    # Add some test data to caches
    user_agent.user_cache = {
        'user1': {'roles': ['user']},
        'user2': {'roles': ['admin']}
    }
    
    # Get metrics
    metrics = user_agent.get_metrics()
    
    # Verify metrics
    assert metrics['status'] == 'success'
    assert metrics['cached_users'] == 2
    assert metrics['admin_users'] == 1
    assert metrics['regular_users'] == 1 