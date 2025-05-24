"""
Tests for the BaseAIAgent class.
"""
import pytest
from datetime import datetime
from unittest.mock import MagicMock
from src.ai.base_agent import BaseAIAgent

class TestAIAgent(BaseAIAgent):
    """Test implementation of BaseAIAgent."""
    async def analyze(self):
        """Test implementation of analyze."""
        return {'test': 'analysis'}
    
    async def act(self, action):
        """Test implementation of act."""
        return True

@pytest.fixture
def mock_client():
    """Create a mock client for testing."""
    return MagicMock()

@pytest.fixture
def ai_agent(mock_client):
    """Create a TestAIAgent instance for testing."""
    return TestAIAgent(mock_client)

def test_init(ai_agent, mock_client):
    """Test initialization of BaseAIAgent."""
    assert ai_agent.client == mock_client
    assert ai_agent._history == []

def test_log_error(ai_agent):
    """Test logging an error."""
    error_message = "Test error message"
    ai_agent._log_error(error_message)
    
    assert len(ai_agent._history) == 1
    log_entry = ai_agent._history[0]
    assert log_entry['type'] == 'error'
    assert log_entry['message'] == error_message
    assert isinstance(log_entry['timestamp'], datetime)

def test_log_info(ai_agent):
    """Test logging an info message."""
    info_message = "Test info message"
    ai_agent._log_info(info_message)
    
    assert len(ai_agent._history) == 1
    log_entry = ai_agent._history[0]
    assert log_entry['type'] == 'info'
    assert log_entry['message'] == info_message
    assert isinstance(log_entry['timestamp'], datetime)

def test_log_warning(ai_agent):
    """Test logging a warning message."""
    warning_message = "Test warning message"
    ai_agent._log_warning(warning_message)
    
    assert len(ai_agent._history) == 1
    log_entry = ai_agent._history[0]
    assert log_entry['type'] == 'warning'
    assert log_entry['message'] == warning_message
    assert isinstance(log_entry['timestamp'], datetime)

def test_get_history(ai_agent):
    """Test getting history."""
    # Add some log entries
    ai_agent._log_error("Error 1")
    ai_agent._log_info("Info 1")
    ai_agent._log_warning("Warning 1")
    
    history = ai_agent.get_history()
    assert len(history) == 3
    assert all(isinstance(entry['timestamp'], datetime) for entry in history)
    assert [entry['type'] for entry in history] == ['error', 'info', 'warning']
    assert [entry['message'] for entry in history] == ['Error 1', 'Info 1', 'Warning 1']

def test_get_recent_history(ai_agent):
    """Test getting recent history."""
    # Add some log entries
    ai_agent._log_error("Error 1")
    ai_agent._log_info("Info 1")
    ai_agent._log_warning("Warning 1")
    
    # Get only error entries
    error_history = ai_agent.get_recent_history(entry_type='error')
    assert len(error_history) == 1
    assert error_history[0]['type'] == 'error'
    assert error_history[0]['message'] == 'Error 1'
    
    # Get only info entries
    info_history = ai_agent.get_recent_history(entry_type='info')
    assert len(info_history) == 1
    assert info_history[0]['type'] == 'info'
    assert info_history[0]['message'] == 'Info 1'

def test_clear_history(ai_agent):
    """Test clearing history."""
    # Add some log entries
    ai_agent._log_error("Error 1")
    ai_agent._log_info("Info 1")
    ai_agent._log_warning("Warning 1")
    
    # Clear history
    ai_agent.clear_history()
    assert len(ai_agent._history) == 0

@pytest.mark.asyncio
async def test_analyze_implementation(ai_agent):
    """Test analyze implementation."""
    result = await ai_agent.analyze()
    assert result == {'test': 'analysis'}

@pytest.mark.asyncio
async def test_act_implementation(ai_agent):
    """Test act implementation."""
    result = await ai_agent.act({'action': 'test'})
    assert result is True

def test_get_timestamp(ai_agent):
    """Test getting timestamp."""
    timestamp = ai_agent._get_timestamp()
    assert isinstance(timestamp, datetime) 