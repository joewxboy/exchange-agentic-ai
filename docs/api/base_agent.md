# Base AI Agent

The `BaseAIAgent` class serves as the foundation for all AI agents in the Open Horizon AI Integration Framework. It provides core functionality for state management, history tracking, and metrics collection, while defining the interface that all specialized agents must implement.

## Class Overview

```python
from src.ai.base import BaseAIAgent
from src.exchange.client import ExchangeAPIClient

class BaseAIAgent(ABC):
    def __init__(self, client: ExchangeAPIClient):
        self.client = client
        self._state = {}
        self._history = []
        self._metrics = {}
```

## Constructor Parameters

- `client` (ExchangeAPIClient): An instance of the Open Horizon Exchange API client used for making API calls.

## Abstract Methods

### analyze

```python
@abstractmethod
async def analyze(self) -> Dict[str, Any]:
    """
    Analyze the current state and generate recommendations.
    
    Returns:
        Dict[str, Any]: A dictionary containing analysis results and recommendations.
    """
    pass
```

This method must be implemented by all subclasses to analyze the current state and generate recommendations for actions.

### act

```python
@abstractmethod
async def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute an action based on the provided action specification.
    
    Args:
        action (Dict[str, Any]): A dictionary specifying the action to execute.
        
    Returns:
        Dict[str, Any]: A dictionary containing the result of the action.
    """
    pass
```

This method must be implemented by all subclasses to execute specific actions based on the analysis results.

## State Management Methods

### update_state

```python
def update_state(self, new_state: Dict[str, Any]) -> None:
    """
    Update the agent's current state.
    
    Args:
        new_state (Dict[str, Any]): The new state to set.
    """
```

Updates the agent's current state with new information.

### get_state

```python
def get_state(self) -> Dict[str, Any]:
    """
    Get the agent's current state.
    
    Returns:
        Dict[str, Any]: The current state.
    """
```

Retrieves the agent's current state.

## History Tracking Methods

### get_history

```python
def get_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get the agent's action history.
    
    Args:
        limit (Optional[int]): Maximum number of history entries to return.
        
    Returns:
        List[Dict[str, Any]]: List of historical actions and their results.
    """
```

Retrieves the agent's action history, optionally limited to a specific number of entries.

## Learning Capabilities

### learn

```python
async def learn(self, experience: Dict[str, Any]) -> None:
    """
    Learn from past experiences to improve future decisions.
    
    Args:
        experience (Dict[str, Any]): The experience to learn from.
    """
```

Updates the agent's knowledge based on past experiences. This is a placeholder for future machine learning implementations.

## Performance Metrics

### get_metrics

```python
def get_metrics(self) -> Dict[str, Any]:
    """
    Get the agent's performance metrics.
    
    Returns:
        Dict[str, Any]: Dictionary containing various performance metrics.
    """
```

Retrieves the agent's performance metrics, including:
- Success rate of actions
- Average response time
- Resource usage
- Error rates

## Usage Example

```python
from src.exchange.client import ExchangeAPIClient
from src.ai.base import BaseAIAgent

# Initialize the API client
client = ExchangeAPIClient(
    base_url="https://exchange.example.com",
    org="myorg",
    username="myuser",
    password="mypassword"
)

# Create a custom agent
class MyAgent(BaseAIAgent):
    async def analyze(self):
        # Implement analysis logic
        return {"recommendations": []}
    
    async def act(self, action):
        # Implement action logic
        return {"result": "success"}

# Initialize and use the agent
agent = MyAgent(client)

# Update state
agent.update_state({"status": "running"})

# Get current state
current_state = agent.get_state()

# Analyze and act
recommendations = await agent.analyze()
result = await agent.act(recommendations["actions"][0])

# Get history
history = agent.get_history(limit=10)

# Get metrics
metrics = agent.get_metrics()
```

## Best Practices

1. **State Management**
   - Keep state updates atomic
   - Validate state data before updates
   - Use appropriate data structures for state

2. **Error Handling**
   - Implement proper error handling in analyze and act methods
   - Log errors for debugging
   - Provide meaningful error messages

3. **Performance**
   - Optimize state updates
   - Cache frequently accessed data
   - Monitor resource usage

4. **Testing**
   - Write unit tests for all methods
   - Test edge cases
   - Verify state consistency

## Related Classes

- `ServiceManagementAgent`: Extends BaseAIAgent for service-specific operations
- `NodeManagementAgent`: Extends BaseAIAgent for node-specific operations
- `ExchangeAPIClient`: Used for API communication 