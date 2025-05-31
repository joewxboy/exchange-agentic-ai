"""
Tests for the Organization Metrics Collector.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.ai.organization_metrics import OrganizationMetricsCollector
from src.organizations import OrganizationInfo, User

@pytest.fixture
def metrics_collector():
    """Create an OrganizationMetricsCollector instance."""
    return OrganizationMetricsCollector()

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
def sample_users():
    """Create sample users for testing."""
    return [
        User(
            username="admin1",
            org_id="test-org",
            roles=["admin"],
            created="2024-01-01T00:00:00Z",
            last_updated="2024-01-01T00:00:00Z"
        ),
        User(
            username="user1",
            org_id="test-org",
            roles=["user"],
            created="2024-01-01T00:00:00Z",
            last_updated="2024-01-01T00:00:00Z"
        ),
        User(
            username="user2",
            org_id="test-org",
            roles=["user"],
            created="2024-01-01T00:00:00Z",
            last_updated="2024-01-01T00:00:00Z"
        )
    ]

def test_collect_metrics(metrics_collector, sample_organization, sample_users):
    """Test metrics collection for an organization."""
    # Prepare test data
    entity_data = {
        'info': sample_organization,
        'users': sample_users,
        'health': {
            'status': 'healthy',
            'message': 'All systems operational'
        }
    }
    
    # Collect metrics
    metrics = metrics_collector.collect_metrics('test-org', entity_data)
    
    # Verify metrics
    assert metrics['org_id'] == 'test-org'
    assert metrics['name'] == sample_organization.name
    assert metrics['total_users'] == 3
    assert metrics['admin_users'] == 1
    assert metrics['super_admin_users'] == 0
    assert metrics['admin_ratio'] == 1/3
    assert metrics['super_admin_ratio'] == 0
    assert metrics['health_status'] == 'healthy'
    assert metrics['health_message'] == 'All systems operational'
    assert metrics['created_at'] == sample_organization.created
    assert metrics['last_updated'] == sample_organization.last_updated

def test_collect_metrics_invalid_data(metrics_collector):
    """Test metrics collection with invalid data."""
    # Test with missing organization info
    metrics = metrics_collector.collect_metrics('test-org', {})
    assert 'error' in metrics
    
    # Test with invalid organization info
    metrics = metrics_collector.collect_metrics('test-org', {'info': 'invalid'})
    assert 'error' in metrics

def test_analyze_metrics(metrics_collector):
    """Test metrics analysis."""
    # Prepare test metrics
    metrics = {
        'total_users': 3,
        'admin_users': 1,
        'admin_ratio': 1/3,
        'activity_score': 0.8,
        'health_status': 'healthy'
    }
    
    # Analyze metrics
    analysis = metrics_collector._analyze_entity_metrics(metrics)
    
    # Verify analysis
    assert analysis['status'] == 'healthy'
    assert analysis['health'] == 'good'
    assert len(analysis['alerts']) == 0
    assert len(analysis['recommendations']) == 0

def test_analyze_metrics_critical(metrics_collector):
    """Test metrics analysis with critical conditions."""
    # Prepare test metrics with critical conditions
    metrics = {
        'total_users': 0,
        'admin_users': 0,
        'admin_ratio': 0,
        'activity_score': 0.1,
        'health_status': 'critical'
    }
    
    # Analyze metrics
    analysis = metrics_collector._analyze_entity_metrics(metrics)
    
    # Verify analysis
    assert analysis['status'] == 'critical'
    assert analysis['health'] == 'critical'
    assert len(analysis['alerts']) > 0
    assert any(alert['level'] == 'critical' for alert in analysis['alerts'])
    assert len(analysis['recommendations']) > 0

def test_analyze_metrics_warning(metrics_collector):
    """Test metrics analysis with warning conditions."""
    # Prepare test metrics with warning conditions
    metrics = {
        'total_users': 3,
        'admin_users': 0,
        'admin_ratio': 0,
        'activity_score': 0.4,
        'health_status': 'warning'
    }
    
    # Analyze metrics
    analysis = metrics_collector._analyze_entity_metrics(metrics)
    
    # Verify analysis
    assert analysis['status'] == 'warning'
    assert analysis['health'] == 'warning'
    assert len(analysis['alerts']) > 0
    assert any(alert['level'] == 'warning' for alert in analysis['alerts'])
    assert len(analysis['recommendations']) > 0

def test_get_trend_analysis(metrics_collector):
    """Test trend analysis."""
    # Add some test metrics to history
    now = datetime.now()
    for i in range(5):
        metrics_collector.metrics_history.append({
            'org_id': 'test-org',
            'timestamp': (now - timedelta(days=i)).isoformat(),
            'total_users': 10 + i,
            'admin_ratio': 0.1 + (i * 0.02),
            'activity_score': 0.5 + (i * 0.1)
        })
    
    # Get trend analysis
    analysis = metrics_collector.get_trend_analysis('test-org', window_days=7)
    
    # Verify analysis
    assert analysis['status'] == 'success'
    assert 'trends' in analysis
    assert 'summary' in analysis
    assert len(analysis['summary']) > 0

def test_get_trend_analysis_no_data(metrics_collector):
    """Test trend analysis with no data."""
    # Get trend analysis for non-existent organization
    analysis = metrics_collector.get_trend_analysis('non-existent', window_days=7)
    
    # Verify analysis
    assert analysis['status'] == 'no_data'
    assert 'message' in analysis

def test_calculate_growth_rate(metrics_collector):
    """Test growth rate calculation."""
    # Create test DataFrame
    import pandas as pd
    df = pd.DataFrame({
        'total_users': [100, 110, 120, 130, 140]
    })
    
    # Calculate growth rate
    growth_rate = metrics_collector._calculate_growth_rate(df, 'total_users')
    
    # Verify growth rate
    assert growth_rate == 0.4  # (140 - 100) / 100

def test_calculate_trend(metrics_collector):
    """Test trend calculation."""
    # Create test DataFrame
    import pandas as pd
    df = pd.DataFrame({
        'activity_score': [0.5, 0.6, 0.7, 0.8, 0.9]
    })
    
    # Calculate trend
    trend = metrics_collector._calculate_trend(df, 'activity_score')
    
    # Verify trend (should be positive)
    assert trend > 0

def test_calculate_health_trend(metrics_collector):
    """Test health trend calculation."""
    # Create test DataFrame
    import pandas as pd
    df = pd.DataFrame({
        'health_status': ['healthy', 'healthy', 'warning', 'healthy', 'critical']
    })
    
    # Calculate health trend
    health_trend = metrics_collector._calculate_health_trend(df)
    
    # Verify health trend
    assert 'healthy_ratio' in health_trend
    assert 'warning_ratio' in health_trend
    assert 'critical_ratio' in health_trend
    assert health_trend['healthy_ratio'] == 0.6
    assert health_trend['warning_ratio'] == 0.2
    assert health_trend['critical_ratio'] == 0.2

def test_generate_trend_summary(metrics_collector):
    """Test trend summary generation."""
    # Prepare test trends
    trends = {
        'user_growth': 0.2,
        'admin_ratio_trend': 0.05,
        'activity_trend': 0.1
    }
    
    # Generate summary
    summary = metrics_collector._generate_trend_summary(trends)
    
    # Verify summary
    assert len(summary) > 0
    assert any(item['type'] == 'positive' for item in summary)
    assert any(item['metric'] == 'user_growth' for item in summary) 