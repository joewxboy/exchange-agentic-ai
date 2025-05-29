import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from src.health import HealthCheck, HealthMonitor, OrganizationHealthMonitor

@pytest.fixture
def health_monitor():
    return HealthMonitor(health_dir="test_health")

@pytest.fixture
def org_health_monitor():
    return OrganizationHealthMonitor(health_dir="test_health")

@pytest.fixture
def mock_client():
    client = Mock()
    return client

def test_health_check_creation():
    """Test creating a health check."""
    check = HealthCheck(
        name="test_check",
        status="healthy",
        message="Test check passed",
        timestamp=datetime.now(),
        details={"test": "data"}
    )
    
    assert check.name == "test_check"
    assert check.status == "healthy"
    assert check.message == "Test check passed"
    assert isinstance(check.timestamp, datetime)
    assert check.details == {"test": "data"}

def test_health_monitor_record_check(health_monitor):
    """Test recording a health check."""
    check = HealthCheck(
        name="test_check",
        status="healthy",
        message="Test check passed",
        timestamp=datetime.now()
    )
    
    health_monitor.record_health_check(check)
    history = health_monitor.get_health_history()
    
    assert len(history) == 1
    assert history[0] == check

def test_health_monitor_get_latest(health_monitor):
    """Test getting the latest health check."""
    check1 = HealthCheck(
        name="test_check1",
        status="healthy",
        message="Test check 1 passed",
        timestamp=datetime.now()
    )
    check2 = HealthCheck(
        name="test_check2",
        status="degraded",
        message="Test check 2 degraded",
        timestamp=datetime.now()
    )
    
    health_monitor.record_health_check(check1)
    health_monitor.record_health_check(check2)
    
    latest = health_monitor.get_latest_health()
    assert latest == check2

@pytest.mark.asyncio
async def test_organization_health_check(org_health_monitor, mock_client):
    """Test checking organization health."""
    # Mock successful responses
    mock_client.get.side_effect = [
        Mock(status_code=200),
        Mock(status_code=200),
        Mock(status_code=200)
    ]
    
    check = await org_health_monitor.check_organization_health("test_org", mock_client)
    
    assert check.name == "organization_health"
    assert check.status == "healthy"
    assert check.message == "Organization is healthy"
    assert isinstance(check.timestamp, datetime)
    assert check.details["org_id"] == "test_org"
    assert "checks" in check.details

@pytest.mark.asyncio
async def test_organization_health_check_failure(org_health_monitor, mock_client):
    """Test organization health check with failure."""
    # Mock failed response
    mock_client.get.return_value = Mock(status_code=404)
    
    check = await org_health_monitor.check_organization_health("test_org", mock_client)
    
    assert check.name == "organization_access"
    assert check.status == "unhealthy"
    assert "Failed to access organization" in check.message
    assert check.details["status_code"] == 404

@pytest.mark.asyncio
async def test_user_health_check(org_health_monitor, mock_client):
    """Test checking user health."""
    # Mock successful response with user data
    mock_client.get.return_value = Mock(
        status_code=200,
        json=lambda: {"roles": ["admin"]}
    )
    
    check = await org_health_monitor.check_user_health("test_org", "test_user", mock_client)
    
    assert check.name == "user_health"
    assert check.status == "healthy"
    assert check.message == "User is healthy"
    assert isinstance(check.timestamp, datetime)
    assert check.details["org_id"] == "test_org"
    assert check.details["username"] == "test_user"
    assert check.details["roles"] == ["admin"]

@pytest.mark.asyncio
async def test_user_health_check_no_roles(org_health_monitor, mock_client):
    """Test user health check with no roles."""
    # Mock response with no roles
    mock_client.get.return_value = Mock(
        status_code=200,
        json=lambda: {"roles": []}
    )
    
    check = await org_health_monitor.check_user_health("test_org", "test_user", mock_client)
    
    assert check.name == "user_permissions"
    assert check.status == "degraded"
    assert "User has no roles assigned" in check.message

def test_health_summary(org_health_monitor):
    """Test getting health summary."""
    # Add some health checks
    checks = [
        HealthCheck("check1", "healthy", "Test 1", datetime.now()),
        HealthCheck("check2", "degraded", "Test 2", datetime.now()),
        HealthCheck("check3", "healthy", "Test 3", datetime.now())
    ]
    
    for check in checks:
        org_health_monitor.record_health_check(check)
    
    summary = org_health_monitor.get_health_summary()
    
    assert summary["status"] == "degraded"
    assert summary["counts"]["healthy"] == 2
    assert summary["counts"]["degraded"] == 1
    assert summary["counts"]["unhealthy"] == 0
    assert summary["total_checks"] == 3

def test_health_summary_empty(org_health_monitor):
    """Test getting health summary with no checks."""
    summary = org_health_monitor.get_health_summary()
    
    assert summary["status"] == "unknown"
    assert "No health checks performed" in summary["message"]
    assert "timestamp" in summary 