from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..exchange_client import ExchangeAPIClient

class BaseAIAgent(ABC):
    """Base class for all AI agents in the Open Horizon system."""
    
    def __init__(self, client: ExchangeAPIClient):
        """Initialize the AI agent with an Exchange API client.
        
        Args:
            client: An instance of ExchangeAPIClient for API interactions
        """
        self.client = client
        self._state: Dict[str, Any] = {}
        self._history: list = []
        
    @abstractmethod
    async def analyze(self) -> Dict[str, Any]:
        """Analyze the current state and make decisions.
        
        Returns:
            Dict containing analysis results and recommended actions
        """
        pass
    
    @abstractmethod
    async def act(self, action: Dict[str, Any]) -> bool:
        """Execute an action based on analysis.
        
        Args:
            action: Dictionary containing action details
            
        Returns:
            bool indicating success or failure
        """
        pass
    
    def update_state(self, new_state: Dict[str, Any]) -> None:
        """Update the agent's internal state.
        
        Args:
            new_state: Dictionary containing new state information
        """
        self._state.update(new_state)
        self._history.append({
            'timestamp': self._get_timestamp(),
            'state': new_state.copy()
        })
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent.
        
        Returns:
            Dict containing current state
        """
        return self._state.copy()
    
    def get_history(self) -> list:
        """Get the history of state changes.
        
        Returns:
            List of state changes with timestamps
        """
        return self._history.copy()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format.
        
        Returns:
            str: ISO formatted timestamp
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    async def learn(self, experience: Dict[str, Any]) -> None:
        """Learn from experience and update internal models.
        
        Args:
            experience: Dictionary containing experience data
        """
        # Base implementation does nothing
        # Subclasses should override to implement learning
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the agent.
        
        Returns:
            Dict containing performance metrics
        """
        return {
            'state_size': len(self._state),
            'history_size': len(self._history),
            'last_update': self._history[-1]['timestamp'] if self._history else None
        } 