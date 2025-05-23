# Open Horizon Exchange API Client

A Python client library for interacting with the Open Horizon Exchange API. This library provides a robust interface for managing services and nodes in an Open Horizon deployment.

## Features

- Secure credential management
- Session-based API communication
- Comprehensive error handling
- Support for all major Exchange API endpoints
- JSON response handling
- Basic authentication support
- **Service management with validation, search, and version listing**
- **Node management with registration, status, update, and deletion**

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/exchange-agentic-ai.git
cd exchange-agentic-ai

# Install dependencies
pip install -r requirements.txt
```

## Configuration

The client can be configured using environment variables:

```bash
# Required environment variables
HZN_ORG_ID=your_org_id
HZN_EXCHANGE_USER_AUTH=your_username:your_password
HZN_EXCHANGE_URL=http://your-exchange-url:port/v1
```

## Usage

### Basic Usage

```python
from src.credentials import CredentialManager
from src.exchange_client import ExchangeAPIClient

# Initialize the credential manager
credential_manager = CredentialManager()

# Create the API client
client = ExchangeAPIClient(credential_manager)

# List services in an organization
services = client.list_services("examples")
print(services)

# Get details of a specific service
service = client.get_service("examples", "web-hello-python")
print(service)
```

### Service Management

```python
from src.services import ServiceManager
from src.exchange_client import ExchangeAPIClient
from src.credentials import CredentialManager

credential_manager = CredentialManager()
client = ExchangeAPIClient(credential_manager)
service_manager = ServiceManager(client)

# Validate service data
service_data = {
    'owner': 'examples/joewxboy',
    'label': 'web-hello-python',
    'description': 'A simple HTTP service',
    'public': True,
    'documentation': 'https://github.com/open-horizon-services/web-helloworld-python/blob/main/README.md',
    'url': 'web-hello-python',
    'version': '1.0.0',
    'arch': 'arm64',
    'sharable': 'singleton',
    'matchHardware': {},
    'requiredServices': [],
    'userInput': [],
    'deployment': {
        'services': {
            'web-hello-python': {
                'image': 'joewxboy/web-hello-python:latest'
            }
        }
    }
}
service_manager.validate_service_data(service_data)

# Create a new service
result = service_manager.create_service('examples', service_data)
print(result)

# Update a service
result = service_manager.update_service('examples', 'web-hello-python', service_data)
print(result)

# Delete a service
result = service_manager.delete_service('examples', 'web-hello-python')
print(result)

# Search for services
results = service_manager.search_services('examples', 'hello')
print(results)

# Get all versions of a service
versions = service_manager.get_service_versions('examples', 'web-hello-python')
print(versions)
```

### Node Management

```python
from src.nodes import NodeManager
from src.exchange_client import ExchangeAPIClient
from src.credentials import CredentialManager

credential_manager = CredentialManager()
client = ExchangeAPIClient(credential_manager)
node_manager = NodeManager(client)

# Validate node data
node_data = {
    'id': 'node1',
    'org_id': 'examples',
    'pattern': 'pattern1',
    'name': 'Test Node',
    'nodeType': 'device',
    'publicKey': 'key123',
    'token': 'token123',
    'registeredServices': [],
    'policy': {}
}
node_manager.validate_node_data(node_data)

# Register a new node
result = node_manager.register_node('examples', node_data)
print(result)

# Get node details
node = node_manager.get_node('examples', 'node1')
print(node)

# Update a node
result = node_manager.update_node('examples', 'node1', node_data)
print(result)

# Delete a node
result = node_manager.delete_node('examples', 'node1')
print(result)

# Get node status
status = node_manager.get_node_status('examples', 'node1')
print(status)
```

### Credential Management

```python
from src.credentials import CredentialManager

# Initialize the credential manager
credential_manager = CredentialManager()

# Request credentials from user
credentials = credential_manager.request_credentials()

# Get headers for API requests
headers = credential_manager.get_headers()
```

## API Reference

### ServiceManager

Manages service-related operations and validation.

#### Methods
- `validate_service_data(service_data)`: Validate service data before creation or update
- `create_service(org_id, service_data)`: Create a new service with validation
- `update_service(org_id, service, service_data)`: Update an existing service with validation
- `delete_service(org_id, service)`: Delete a service (with planned dependency checks)
- `search_services(org_id, query)`: Search for services matching the query
- `get_service_versions(org_id, service)`: Get all versions of a service

### NodeManager

Manages node-related operations and validation.

#### Methods
- `validate_node_data(node_data)`: Validate node data before registration or update
- `register_node(org_id, node_data)`: Register a new node with validation
- `get_node(org_id, node_id)`: Get details of a specific node
- `update_node(org_id, node_id, node_data)`: Update an existing node with validation
- `delete_node(org_id, node_id)`: Delete a node
- `get_node_status(org_id, node_id)`: Get node status (heartbeat, services, policy)

### ExchangeAPIClient

The main client class for interacting with the Exchange API.

#### Methods
- `list_organizations()`: Get a list of all organizations
- `get_organization(org_id)`: Get details of a specific organization
- `list_services(org_id)`: Get a list of services in an organization
- `get_service(org_id, service)`: Get details of a specific service
- `create_service(org_id, service_data)`: Create a new service
- `update_service(org_id, service, service_data)`: Update an existing service
- `delete_service(org_id, service)`: Delete a service
- `list_nodes(org_id)`: Get a list of nodes in an organization
- `get_node(org_id, node_id)`: Get details of a specific node
- `create_node(org_id, node_data)`: Create a new node
- `update_node(org_id, node_id, node_data)`: Update an existing node
- `delete_node(org_id, node_id)`: Delete a node

### CredentialManager

Manages API credentials with secure storage and validation.

#### Methods
- `request_credentials()`: Securely request credentials from the user
- `get_credentials()`: Get the current credentials
- `clear_credentials()`: Clear stored credentials
- `validate_credentials()`: Validate the current credentials
- `get_headers(method="GET")`: Get headers for API requests
- `get_base_url()`: Get the base URL for API requests

## Error Handling

The client includes comprehensive error handling:

- Invalid credentials
- Network errors
- API errors
- JSON parsing errors

All errors are wrapped in `ExchangeAPIError` exceptions with descriptive messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Development Status

Current implementation status:
- ✅ Basic client structure
- ✅ Authentication handling
- ✅ URL construction
- ✅ Error handling
- ✅ Session management
- ✅ Credential management
- ✅ Unit tests
- ✅ Service management
- ✅ Node management
- 🔄 Documentation (in progress)