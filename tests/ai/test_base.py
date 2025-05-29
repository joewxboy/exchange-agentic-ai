"""
Unit tests for the base AI agent implementation.
"""
import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from src.ai.base import BaseAIAgent

class TestBaseAIAgent:
    """Test cases for BaseAIAgent."""
    
    @pytest.fixture
    def mock_client(self):
        """Create a mock ExchangeAPIClient."""
        return Mock()
    
    @pytest.fixture
    def agent(self, mock_client):
        """Create a test instance of BaseAIAgent."""
        class TestAgent(BaseAIAgent):
            async def analyze(self):
                return {'status': 'test'}
            
            async def act(self, action):
                return True
        
        return TestAgent(mock_client)
    
    def test_initialization(self, mock_client):
        """Test agent initialization."""
        class TestAgent(BaseAIAgent):
            async def analyze(self):
                return {'status': 'test'}
            async def act(self, action):
                return True
        agent = TestAgent(mock_client)
        assert agent.client == mock_client
        assert agent.config == {}
        assert agent._state == {}
        assert agent._history == []
    
    def test_initialization_with_config(self, mock_client):
        """Test agent initialization with configuration."""
        config = {'test': 'config'}
        class TestAgent(BaseAIAgent):
            async def analyze(self):
                return {'status': 'test'}
            async def act(self, action):
                return True
        agent = TestAgent(mock_client, config)
        assert agent.config == config
    
    def test_update_state(self, agent):
        """Test state update functionality."""
        new_state = {'test': 'state'}
        agent.update_state(new_state)
        assert agent._state == new_state
        assert len(agent._history) == 1
        assert agent._history[0]['state'] == new_state
    
    def test_get_state(self, agent):
        """Test state retrieval."""
        test_state = {'test': 'state'}
        agent._state = test_state
        assert agent.get_state() == test_state
    
    def test_get_history(self, agent):
        """Test history retrieval."""
        test_history = [{'timestamp': 'test', 'state': {'test': 'state'}}]
        agent._history = test_history
        assert agent.get_history() == test_history
    
    def test_get_metrics(self, agent):
        """Test metrics retrieval."""
        agent._state = {'test': 'state'}
        agent._history = [{'timestamp': 'test', 'state': {'test': 'state'}}]
        metrics = agent.get_metrics()
        assert metrics['state_size'] == 1
        assert metrics['history_size'] == 1
        assert metrics['last_update'] == 'test'
    
    @pytest.mark.asyncio
    async def test_learn(self, agent):
        """Test learning functionality."""
        experience = {'test': 'experience'}
        await agent.learn(experience)
        # Since _process_experience is not implemented in base class,
        # we just verify no errors occurred
    
    def test_log_error(self, agent):
        """Test error logging."""
        error_message = "Test error"
        agent._log_error(error_message)
        assert len(agent._history) == 1
        assert agent._history[0]['type'] == 'error'
        assert agent._history[0]['message'] == error_message 