# Node Management Agent

The `NodeManagementAgent` class extends the `BaseAIAgent` to provide specialized functionality for managing Open Horizon nodes. It handles node health monitoring, resource tracking, and automated node management actions.

## Class Overview

```python
from src.ai.node_agent import NodeManagementAgent
from src.exchange.client import ExchangeAPIClient

class NodeManagementAgent(BaseAIAgent):
    def __init__(self, client: ExchangeAPIClient, config: Optional[Dict[str, Any]] = None):
        super().__init__(client, config)
        self._metrics_collector = NodeMetricsCollector(config)
        self._health_history: List[Dict[str, Any]] = []
```

## Constructor Parameters

- `client` (ExchangeAPIClient): An instance of the Open Horizon Exchange API client used for making API calls.
- `config` (Optional[Dict[str, Any]]): Optional configuration dictionary for customizing agent behavior.

## Core Methods

### analyze

```python
async def analyze(self) -> Dict[str, Any]:
    """
    Analyze the current state of nodes and generate recommendations.
    
    Returns:
        Dict[str, Any]: A dictionary containing:
            - nodes: List of analyzed nodes
            - recommendations: List of recommended actions
            - alerts: List of alerts and warnings
    """
```

### act

```python
async def act(self, action: Dict[str, Any]) -> bool:
    """
    Execute a node management action.
    
    Args:
        action (Dict[str, Any]): Action specification containing:
            - action: Action type ('check_health', 'update', 'cleanup')
            - node_id: ID of the node to act upon
            - update_data: Additional data for update actions
            
    Returns:
        bool: Success or failure of the action
    """
```

## Node Management Methods

### register_node

```python
async def register_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a new node in the Exchange.
    
    Args:
        node_data (Dict[str, Any]): Node registration data containing:
            - name: Node name
            - nodeType: Type of node
            - publicKey: Node's public key
            - token: Authentication token
            - registeredServices: List of registered services
            - policy: Node policy configuration
            
    Returns:
        Dict[str, Any]: Registration result containing:
            - status: 'success' or 'error'
            - node_id: ID of registered node (if successful)
            - message: Status message or error details
    """
```

### delete_node

```python
async def delete_node(self, node_id: str) -> Dict[str, Any]:
    """
    Delete a node from the Exchange.
    
    Args:
        node_id (str): ID of the node to delete
        
    Returns:
        Dict[str, Any]: Deletion result containing:
            - status: 'success' or 'error'
            - message: Status message or error details
    """
```

### get_node_status

```python
async def get_node_status(self, node_id: str) -> Dict[str, Any]:
    """
    Get detailed status information for a specific node.
    
    Args:
        node_id (str): ID of the node to check
        
    Returns:
        Dict[str, Any]: Node status information containing:
            - status: Current node status
            - health: Node health status
            - metrics: Current node metrics
            - trends: Resource usage trends
    """
```

## Internal Methods

### _check_node_health

```python
async def _check_node_health(self, node_id: str) -> bool:
    """
    Check the health of a node.
    
    Args:
        node_id (str): ID of the node to check
        
    Returns:
        bool: Success or failure of the health check
    """
```

### _update_node

```python
async def _update_node(self, node_id: str, update_data: Dict[str, Any]) -> bool:
    """
    Update a node with new configuration.
    
    Args:
        node_id (str): ID of the node to update
        update_data (Dict[str, Any]): New configuration data
        
    Returns:
        bool: Success or failure of the update
    """
```

### _cleanup_node

```python
async def _cleanup_node(self, node_id: str) -> bool:
    """
    Clean up a node's disk space.
    
    Args:
        node_id (str): ID of the node to clean up
        
    Returns:
        bool: Success or failure of the cleanup
    """
```

## Usage Example

```python
from src.exchange.client import ExchangeAPIClient
from src.ai.node_agent import NodeManagementAgent

# Initialize the API client
client = ExchangeAPIClient(
    base_url="https://exchange.example.com",
    org="myorg",
    username="myuser",
    password="mypassword"
)

# Create node management agent
node_agent = NodeManagementAgent(client)

# Register a new node
node_data = {
    'name': 'example-node',
    'nodeType': 'device',
    'publicKey': 'your-public-key',
    'token': 'your-token',
    'registeredServices': [],
    'policy': {
        'deployment': {
            'constraints': ['cpu >= 2', 'memory >= 4GB']
        }
    }
}
registration = await node_agent.register_node(node_data)

# Get node status
status = await node_agent.get_node_status(registration['node_id'])

# Analyze nodes
analysis = await node_agent.analyze()

# Execute recommended actions
for action in analysis["recommendations"]:
    result = await node_agent.act(action)
    print(f"Action result: {result}")

# Delete node if needed
if status['health'] == 'critical':
    result = await node_agent.delete_node(registration['node_id'])
    print(f"Node deletion: {result['message']}")
```

## Best Practices

1. **Node Registration**
   - Validate node data before registration
   - Handle registration errors appropriately
   - Store node credentials securely
   - Implement retry mechanisms for network issues

2. **Node Monitoring**
   - Set appropriate monitoring intervals
   - Define meaningful thresholds
   - Monitor multiple metrics
   - Track historical data

3. **Resource Management**
   - Set resource limits
   - Monitor resource usage
   - Implement cleanup procedures
   - Optimize resource allocation

4. **Error Handling**
   - Implement retry mechanisms
   - Log error details
   - Set up alerts
   - Document recovery procedures

5. **Performance Optimization**
   - Cache frequently accessed data
   - Optimize API calls
   - Monitor response times
   - Track resource usage

## Related Classes

- `BaseAIAgent`: Parent class providing core functionality
- `NodeMetricsCollector`: Handles node metrics collection and analysis
- `ExchangeAPIClient`: Used for API communication

## Configuration

The NodeManagementAgent can be configured through environment variables:

```bash
# Node monitoring interval (in seconds)
NODE_MONITOR_INTERVAL=60

# Resource thresholds
CPU_THRESHOLD=80
MEMORY_THRESHOLD=85
DISK_THRESHOLD=90
TEMPERATURE_THRESHOLD=75

# Retry configuration
MAX_RETRIES=3
RETRY_DELAY=5
```

## Error Codes

Common error codes and their meanings:

- `NODE_NOT_FOUND`: Node does not exist
- `INVALID_ACTION`: Action type is not supported
- `RESOURCE_LIMIT`: Resource limit exceeded
- `TEMPERATURE_ERROR`: Node temperature too high
- `DISK_SPACE_ERROR`: Insufficient disk space
- `PERMISSION_DENIED`: Insufficient permissions
- `VALIDATION_ERROR`: Invalid node data
- `REGISTRATION_ERROR`: Node registration failed
- `DELETION_ERROR`: Node deletion failed 