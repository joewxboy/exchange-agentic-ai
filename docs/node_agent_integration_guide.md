# NodeManagementAgent Integration Guide

This guide provides comprehensive documentation and examples for using the NodeManagementAgent with various AI frameworks and tools.

## Table of Contents
1. [Basic Usage](#1-basic-usage)
2. [LangChain Integration](#2-langchain-integration)
3. [LangFlow Integration](#3-langflow-integration)
4. [BeeAI Integration](#4-beeai-integration)
5. [n8n Integration](#5-n8n-integration)
6. [Advanced Usage](#6-advanced-usage)
7. [Configuration](#7-configuration)
8. [Error Handling](#8-error-handling)

## 1. Basic Usage

```python
from src.exchange.client import ExchangeAPIClient
from src.ai.node_agent import NodeManagementAgent
from src.credentials import CredentialManager

# Initialize components
credential_manager = CredentialManager()
client = ExchangeAPIClient(credential_manager)
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
print(registration)  # Contains status, node_id, and message

# Analyze nodes
analysis = await node_agent.analyze()
print(analysis)  # Contains nodes, recommendations, and alerts

# Get node status
status = await node_agent.get_node_status('node-id')
print(status)  # Contains status, health, metrics, and trends

# Delete a node
result = await node_agent.delete_node('node-id')
print(result)  # Contains status and message
```

## 2. LangChain Integration

```python
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from src.ai.node_agent import NodeManagementAgent

# Initialize NodeManagementAgent
node_agent = NodeManagementAgent(client)

# Create LangChain tools
tools = [
    Tool(
        name="analyze_nodes",
        func=node_agent.analyze,
        description="Analyze Open Horizon nodes and get recommendations"
    ),
    Tool(
        name="update_node",
        func=lambda x: node_agent.act({
            'action': 'update',
            'node_id': x['node_id'],
            'update_data': x['update_data']
        }),
        description="Update an Open Horizon node"
    )
]

# Create custom prompt template
class NodePromptTemplate(StringPromptTemplate):
    template = """You are an AI assistant managing Open Horizon nodes.
    
    Current state: {state}
    Available tools: {tools}
    Question: {input}
    {agent_scratchpad}"""

# Initialize agent
prompt = NodePromptTemplate()
agent = LLMSingleActionAgent(
    llm_chain=LLMChain(llm=your_llm, prompt=prompt),
    allowed_tools=[tool.name for tool in tools]
)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True
)

# Use the agent
response = agent_executor.run("Check node health and update if needed")
```

## 3. LangFlow Integration

```python
from langflow import load_flow_from_json
from src.ai.node_agent import NodeManagementAgent

# Define the flow in JSON
flow_config = {
    "nodes": [
        {
            "id": "node_metrics",
            "type": "NodeMetricsCollector",
            "data": {
                "analysis_window": "30m"
            }
        },
        {
            "id": "node_agent",
            "type": "NodeManagementAgent",
            "data": {
                "client": "exchange_client"
            }
        }
    ],
    "edges": [
        {
            "source": "node_metrics",
            "target": "node_agent",
            "type": "metrics_to_agent"
        }
    ]
}

# Load and run the flow
flow = load_flow_from_json(flow_config)
result = flow.run()
```

## 4. BeeAI Integration

```python
from beeai import BeeAI
from src.ai.node_agent import NodeManagementAgent

# Initialize BeeAI
bee = BeeAI()

# Register Open Horizon components
@bee.component
class OpenHorizonNode:
    def __init__(self):
        self.agent = NodeManagementAgent(client)

    @bee.action
    def analyze_nodes(self):
        return self.agent.analyze()

    @bee.action
    def update_node(self, node_id: str, update_data: dict):
        return self.agent.act({
            'action': 'update',
            'node_id': node_id,
            'update_data': update_data
        })

# Use the component
node = OpenHorizonNode()
analysis = node.analyze_nodes()
```

## 5. n8n Integration

```python
from n8n import Node, Workflow
from src.ai.node_agent import NodeManagementAgent

# Create n8n node
class OpenHorizonNode(Node):
    def __init__(self):
        self.agent = NodeManagementAgent(client)

    def execute(self, input_data):
        if input_data.get('action') == 'analyze':
            return self.agent.analyze()
        elif input_data.get('action') == 'update':
            return self.agent.act({
                'action': 'update',
                'node_id': input_data['node_id'],
                'update_data': input_data['update_data']
            })

# Create workflow
workflow = Workflow()
workflow.add_node(OpenHorizonNode())
```

## 6. Advanced Usage

### 6.1. Multiple Agents
```python
from src.exchange.client import ExchangeAPIClient
from src.ai.service_agent import ServiceManagementAgent
from src.ai.node_agent import NodeManagementAgent

# Initialize agents
client = ExchangeAPIClient(credential_manager)
service_agent = ServiceManagementAgent(client)
node_agent = NodeManagementAgent(client)

# Analyze and act on both services and nodes
service_analysis = await service_agent.analyze()
node_analysis = await node_agent.analyze()

# Respond to recommendations
for rec in service_analysis.get('recommendations', []):
    await service_agent.act(rec)
for rec in node_analysis.get('recommendations', []):
    await node_agent.act(rec)
```

### 6.2. Custom Metrics Collection
```python
from src.ai.node_metrics import NodeMetricsCollector
from datetime import timedelta

# Initialize custom metrics collector
metrics_collector = NodeMetricsCollector(
    analysis_window=timedelta(minutes=30),
    thresholds={
        'cpu': 80,
        'memory': 85,
        'disk': 90,
        'temperature': 75
    }
)

# Use with NodeManagementAgent
node_agent = NodeManagementAgent(client, config={'metrics_collector': metrics_collector})
```

### 6.3. Node Registration and Management
```python
# Register a new node with validation
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

# Register node
registration = await node_agent.register_node(node_data)
if registration['status'] == 'success':
    node_id = registration['node_id']
    
    # Get node status
    status = await node_agent.get_node_status(node_id)
    print(f"Node status: {status['status']}")
    print(f"Health: {status['health']}")
    print(f"Metrics: {status['metrics']}")
    
    # Delete node if needed
    if status['health'] == 'critical':
        result = await node_agent.delete_node(node_id)
        print(f"Node deletion: {result['message']}")
```

### 6.4. Error Handling and Validation
```python
try:
    # Register node with invalid data
    invalid_data = {
        'name': 'example-node',
        # Missing required fields
    }
    result = await node_agent.register_node(invalid_data)
    print(f"Registration failed: {result['message']}")
    
    # Delete non-existent node
    result = await node_agent.delete_node('non-existent-node')
    print(f"Deletion failed: {result['message']}")
    
    # Get status of non-existent node
    status = await node_agent.get_node_status('non-existent-node')
    print(f"Status check failed: {status['message']}")
    
except Exception as e:
    print(f"Error: {str(e)}")
```

## 7. Configuration

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

## 8. Error Handling

```python
try:
    analysis = await node_agent.analyze()
    for alert in analysis.get('alerts', []):
        print(f"ALERT: {alert['message']}")
        if alert['type'] == 'critical':
            # Handle critical alerts
            await node_agent.act({
                'action': 'check_health',
                'node_id': alert['node_id']
            })
except Exception as e:
    print(f"Error analyzing nodes: {str(e)}")
```

## Best Practices

1. **Error Handling**
   - Always wrap agent operations in try-except blocks
   - Log errors with appropriate context
   - Implement retry mechanisms for transient failures
   - Validate node data before registration
   - Check node existence before operations

2. **Resource Management**
   - Monitor resource usage during agent operations
   - Implement cleanup procedures for temporary resources
   - Set appropriate timeouts for long-running operations
   - Clean up unused nodes to prevent resource waste

3. **Configuration**
   - Use environment variables for configuration
   - Document all configuration options
   - Provide sensible defaults
   - Set appropriate thresholds for node health checks

4. **Testing**
   - Write unit tests for agent operations
   - Mock external dependencies
   - Test error handling scenarios
   - Test node registration and deletion workflows
   - Test status monitoring and health checks

5. **Monitoring**
   - Log important operations
   - Track performance metrics
   - Monitor resource usage
   - Track node registration and deletion events
   - Monitor node health status changes

## Related Documentation

- [Base AI Agent](api/base_agent.md)
- [Node Metrics Collector](api/node_metrics_collector.md)
- [Configuration Guide](configuration_guide.md)
- [Troubleshooting Guide](troubleshooting_guide.md) 