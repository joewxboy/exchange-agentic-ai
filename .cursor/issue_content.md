# Add Node Registration to NodeManagementAgent

## Description
The NodeManagementAgent currently lacks the ability to register new nodes with the Open Horizon Exchange. This feature will add node registration capabilities to the agent, allowing it to create and register new nodes in the system.

## Current Behavior
- NodeManagementAgent can monitor and manage existing nodes
- No functionality to register new nodes
- Node registration must be done through other means

## Proposed Changes
Add a new `register_node` method to NodeManagementAgent that will:
1. Validate node registration data
2. Handle node registration through the Exchange API
3. Process registration responses and errors
4. Return registration status and node ID

## Implementation Details
### New Method
```python
async def register_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Register a new node with the Open Horizon Exchange.
    
    Args:
        node_data: Dictionary containing node registration data including:
            - name: Node name
            - nodeType: Type of node
            - publicKey: Node's public key
            - token: Registration token
            - registeredServices: List of services
            - policy: Node policy configuration
            
    Returns:
        Dict containing:
            - status: Registration status
            - node_id: ID of registered node
            - message: Status message
    """
```

### Test Cases
1. Successful node registration
   - Valid node data
   - Proper API response
   - Correct node ID returned

2. Data validation
   - Invalid node data
   - Missing required fields
   - Invalid field types

3. Error handling
   - Invalid credentials
   - Duplicate node names
   - Network errors
   - API errors

4. Edge cases
   - Empty service list
   - Minimal policy configuration
   - Maximum field lengths

## Success Criteria
- [ ] All test cases pass
- [ ] Successfully registers new nodes with Exchange API
- [ ] Validates node data before registration
- [ ] Handles registration errors appropriately
- [ ] Returns registration status and node ID
- [ ] Documentation updated
- [ ] Code follows project style guidelines

## Dependencies
- ExchangeAPIClient
- NodeMetricsCollector
- Existing node validation logic

## Related Issues
- None

## Additional Notes
- Follow existing error handling patterns
- Maintain consistent logging
- Update integration tests
- Add example usage to documentation

# Node Deletion in NodeManagementAgent

## Description
Currently, the `NodeManagementAgent` does not support deleting nodes from the Open Horizon Exchange. This feature is required for full lifecycle management of nodes.

## Current Behavior
- Nodes can be analyzed, updated, and cleaned up, but not deleted via the agent.

## Proposed Changes
- Add a `delete_node` method to `NodeManagementAgent`.
- The method should:
  - Validate input (node_id required, must be a string)
  - Call the appropriate method on the ExchangeAPIClient
  - Handle errors (e.g., node not found, API errors)
  - Return a status dictionary with success/failure and a message

## Implementation Details
```python
async def delete_node(self, node_id: str) -> Dict[str, Any]:
    """Delete a node from the Exchange."""
    # Implementation will validate input, call client.delete_node, and handle errors
```

## Test Cases
- `test_delete_node_success`: Node is deleted successfully
- `test_delete_node_not_found`: Node does not exist
- `test_delete_node_invalid_id`: node_id is missing or not a string
- `test_delete_node_api_error`: API error occurs during deletion
- `test_delete_node_edge_cases`: Deleting a node with dependencies, etc.

## Success Criteria
- All tests for node deletion pass
- Method handles all error cases gracefully
- Documentation and usage examples updated if needed

## Dependencies
- ExchangeAPIClient must have a working `delete_node` method

## Related Issues
- #11 (Node Registration)

## Additional Notes
- Follow the same TDD and workflow as previous features

# Node Status Management in NodeManagementAgent

## Description
Currently, the `NodeManagementAgent` does not provide a dedicated method to retrieve detailed status information for a specific node. This feature will add a `get_node_status` method to the agent, allowing users to query the current status, health, and metrics of a node.

## Current Behavior
- The agent can analyze nodes in bulk and perform actions, but lacks a direct method to get detailed status for a single node.

## Proposed Changes
- Add a `get_node_status` method to `NodeManagementAgent`.
- The method should:
  - Validate input (node_id required, must be a string)
  - Call the appropriate method on the ExchangeAPIClient to retrieve node data
  - Process and return detailed status information (e.g., status, health, metrics, trends)
  - Handle errors (e.g., node not found, API errors)

## Implementation Details
```python
async def get_node_status(self, node_id: str) -> Dict[str, Any]:
    """Get detailed status information for a specific node."""
    # Implementation will validate input, call client.get_node, and process the response
```

## Test Cases
- `test_get_node_status_success`: Node status is retrieved successfully
- `test_get_node_status_not_found`: Node does not exist
- `test_get_node_status_invalid_id`: node_id is missing or not a string
- `test_get_node_status_api_error`: API error occurs during retrieval
- `test_get_node_status_edge_cases`: Node with minimal or unusual status data

## Success Criteria
- All tests for node status retrieval pass
- Method handles all error cases gracefully
- Documentation and usage examples updated if needed

## Dependencies
- ExchangeAPIClient must have a working `get_node` method

## Related Issues
- #11 (Node Registration)
- #13 (Node Deletion)

## Additional Notes
- Follow the same TDD and workflow as previous features

# Node Service Management

## Description
Currently, the `NodeManagementAgent` lacks functionality to retrieve the list of services running on a specific node. This feature is essential for monitoring and managing node services effectively.

## Current Behavior
The `NodeManagementAgent` does not have a method to retrieve node services, limiting its ability to provide comprehensive node management.

## Proposed Changes
Add a new method `get_node_services` to `NodeManagementAgent` that:
- Validates the node_id input.
- Calls the `ExchangeAPIClient` to retrieve the list of services for the specified node.
- Returns detailed service information, including service names, versions, and statuses.
- Handles errors appropriately, such as node not found or API errors.

## Implementation Details
```python
async def get_node_services(self, node_id: str) -> Dict[str, Any]:
    """Get the list of services running on a specific node."""
    if not isinstance(node_id, str):
        return {'status': 'error', 'message': 'node_id must be a string'}
    try:
        services = await self.client.get_node_services(node_id)
        return {
            'status': 'success',
            'services': services
        }
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
```

## Test Cases
- **Successful Retrieval**: Test that the method returns the correct list of services for a valid node_id.
- **Node Not Found**: Test the behavior when the node_id does not exist.
- **Invalid Node ID**: Test the behavior when the node_id is invalid (missing or not a string).
- **API Error**: Test the behavior when an API error occurs during the retrieval.

## Success Criteria
- The `get_node_services` method successfully retrieves and returns the list of services for a valid node_id.
- The method handles errors gracefully and returns appropriate error messages.

## Dependencies
- `ExchangeAPIClient` must have a `get_node_services` method implemented to retrieve the services from the Exchange API.

## Related Issues
- None

## Additional Notes
- This feature is part of the ongoing enhancement of the `NodeManagementAgent` to provide comprehensive node management capabilities. 