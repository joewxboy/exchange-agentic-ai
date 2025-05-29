"""
Base class for all AI agents in the Open Horizon system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from ..exchange_client import ExchangeAPIClient

class BaseAIAgent(ABC):
    """Base class for all AI agents in the Open Horizon system."""
    
    def __init__(self, client: ExchangeAPIClient, config: Optional[Dict[str, Any]] = None):
        """Initialize the AI agent with an Exchange API client.
        
        Args:
            client: An instance of ExchangeAPIClient for API interactions
            config: Optional configuration dictionary
        """
        self.client = client
        self.config = config or {}
        self._state: Dict[str, Any] = {}
        self._history: List[Dict[str, Any]] = []
        self.logger = logging.getLogger(self.__class__.__name__)
        
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
        try:
            self._state.update(new_state)
            self._history.append({
                'timestamp': self._get_timestamp(),
                'state': new_state.copy()
            })
            self.logger.debug(f"State updated: {new_state}")
        except Exception as e:
            self.logger.error(f"Failed to update state: {str(e)}")
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the agent.
        
        Returns:
            Dict containing current state
        """
        return self._state.copy()
    
    def get_history(self) -> List[Dict[str, Any]]:
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
        return datetime.utcnow().isoformat()
    
    async def learn(self, experience: Dict[str, Any]) -> None:
        """Learn from experience and update internal models.
        
        Args:
            experience: Dictionary containing experience data
        """
        try:
            await self._process_experience(experience)
            self.logger.debug(f"Processed experience: {experience}")
        except Exception as e:
            self.logger.error(f"Failed to process experience: {str(e)}")
    
    async def _process_experience(self, experience: Dict[str, Any]) -> None:
        """Process experience data. To be implemented by subclasses.
        
        Args:
            experience: Dictionary containing experience data
        """
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the agent.
        
        Returns:
            Dict containing performance metrics
        """
        return {
            'state_size': len(self._state),
            'history_size': len(self._history),
            'last_update': self._history[-1]['timestamp'] if self._history else None,
            'config': self.config
        }
    
    def _log_error(self, error_message: str) -> None:
        """Log an error message.
        
        Args:
            error_message: Error message to log
        """
        self.logger.error(error_message)
        self._history.append({
            'timestamp': self._get_timestamp(),
            'type': 'error',
            'message': error_message
        }) 