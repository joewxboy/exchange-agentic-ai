# ServiceManagementAgent Integration Guide

This guide provides comprehensive documentation and examples for using the ServiceManagementAgent with various AI frameworks and tools.

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
from src.ai.service_agent import ServiceManagementAgent
from src.credentials import CredentialManager

# Initialize components
credential_manager = CredentialManager()
client = ExchangeAPIClient(credential_manager)
service_agent = ServiceManagementAgent(client)

# Analyze services
analysis = await service_agent.analyze()
print(analysis)  # Contains services, recommendations, and alerts
```

## 2. LangChain Integration

```python
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from src.ai.service_agent import ServiceManagementAgent

# Initialize ServiceManagementAgent
service_agent = ServiceManagementAgent(client)

# Create LangChain tools
tools = [
    Tool(
        name="analyze_services",
        func=service_agent.analyze,
        description="Analyze Open Horizon services and get recommendations"
    ),
    Tool(
        name="update_service",
        func=lambda x: service_agent.act({
            'action': 'update',
            'service_id': x['service_id'],
            'update_data': x['update_data']
        }),
        description="Update an Open Horizon service"
    ),
    Tool(
        name="deploy_service",
        func=lambda x: service_agent.act({
            'action': 'deploy',
            'service_id': x['service_id'],
            'deployment_config': x['deployment_config']
        }),
        description="Deploy a service to nodes"
    )
]

# Create custom prompt template
class ServicePromptTemplate(StringPromptTemplate):
    template = """You are an AI assistant managing Open Horizon services.
    
    Current state: {state}
    Available tools: {tools}
    Question: {input}
    {agent_scratchpad}"""

# Initialize agent
prompt = ServicePromptTemplate()
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
response = agent_executor.run("Check service health and update if needed")
```

## 3. LangFlow Integration

```python
from langflow import load_flow_from_json
from src.ai.service_agent import ServiceManagementAgent

# Define the flow in JSON
flow_config = {
    "nodes": [
        {
            "id": "service_metrics",
            "type": "ServiceMetricsCollector",
            "data": {
                "analysis_window": "30m"
            }
        },
        {
            "id": "service_agent",
            "type": "ServiceManagementAgent",
            "data": {
                "client": "exchange_client"
            }
        }
    ],
    "edges": [
        {
            "source": "service_metrics",
            "target": "service_agent",
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
from src.ai.service_agent import ServiceManagementAgent

# Initialize BeeAI
bee = BeeAI()

# Register Open Horizon components
@bee.component
class OpenHorizonService:
    def __init__(self):
        self.agent = ServiceManagementAgent(client)

    @bee.action
    def analyze_services(self):
        return self.agent.analyze()

    @bee.action
    def update_service(self, service_id: str, update_data: dict):
        return self.agent.act({
            'action': 'update',
            'service_id': service_id,
            'update_data': update_data
        })

    @bee.action
    def deploy_service(self, service_id: str, deployment_config: dict):
        return self.agent.act({
            'action': 'deploy',
            'service_id': service_id,
            'deployment_config': deployment_config
        })

# Use the component
service = OpenHorizonService()
analysis = service.analyze_services()
```

## 5. n8n Integration

```python
from n8n import Node, Workflow
from src.ai.service_agent import ServiceManagementAgent

# Create n8n node
class OpenHorizonService(Node):
    def __init__(self):
        self.agent = ServiceManagementAgent(client)

    def execute(self, input_data):
        if input_data.get('action') == 'analyze':
            return self.agent.analyze()
        elif input_data.get('action') == 'update':
            return self.agent.act({
                'action': 'update',
                'service_id': input_data['service_id'],
                'update_data': input_data['update_data']
            })
        elif input_data.get('action') == 'deploy':
            return self.agent.act({
                'action': 'deploy',
                'service_id': input_data['service_id'],
                'deployment_config': input_data['deployment_config']
            })

# Create workflow
workflow = Workflow()
workflow.add_node(OpenHorizonService())
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
from src.ai.service_metrics import ServiceMetricsCollector
from datetime import timedelta

# Initialize custom metrics collector
metrics_collector = ServiceMetricsCollector(
    analysis_window=timedelta(minutes=30),
    thresholds={
        'cpu': 80,
        'memory': 85,
        'response_time': 1000,
        'error_rate': 0.05
    }
)

# Use with ServiceManagementAgent
service_agent = ServiceManagementAgent(client, config={'metrics_collector': metrics_collector})
```

### 6.3. Service Deployment
```python
# Deploy a service to specific nodes
deployment_config = {
    'nodes': ['node1', 'node2'],
    'version': '1.0.0',
    'config': {
        'environment': 'production',
        'resources': {
            'cpu': 2,
            'memory': '4Gi'
        }
    }
}

result = await service_agent.act({
    'action': 'deploy',
    'service_id': 'my-service',
    'deployment_config': deployment_config
})
```

## 7. Configuration

The ServiceManagementAgent can be configured through environment variables:

```bash
# Service monitoring interval (in seconds)
SERVICE_MONITOR_INTERVAL=60

# Resource thresholds
SERVICE_CPU_THRESHOLD=80
SERVICE_MEMORY_THRESHOLD=85
SERVICE_RESPONSE_TIME_THRESHOLD=1000
SERVICE_ERROR_RATE_THRESHOLD=0.05

# Deployment configuration
SERVICE_DEPLOYMENT_TIMEOUT=300
SERVICE_ROLLBACK_ENABLED=true
SERVICE_HEALTH_CHECK_INTERVAL=30

# Retry configuration
MAX_RETRIES=3
RETRY_DELAY=5
```

## 8. Error Handling

```python
try:
    analysis = await service_agent.analyze()
    for alert in analysis.get('alerts', []):
        print(f"ALERT: {alert['message']}")
        if alert['type'] == 'critical':
            # Handle critical alerts
            await service_agent.act({
                'action': 'check_health',
                'service_id': alert['service_id']
            })
except Exception as e:
    print(f"Error analyzing services: {str(e)}")
```

## Best Practices

1. **Error Handling**
   - Always wrap agent operations in try-except blocks
   - Log errors with appropriate context
   - Implement retry mechanisms for transient failures
   - Handle deployment failures gracefully

2. **Resource Management**
   - Monitor resource usage during service operations
   - Implement cleanup procedures for temporary resources
   - Set appropriate timeouts for long-running operations
   - Monitor service dependencies

3. **Configuration**
   - Use environment variables for configuration
   - Document all configuration options
   - Provide sensible defaults
   - Version control service configurations

4. **Testing**
   - Write unit tests for agent operations
   - Mock external dependencies
   - Test error handling scenarios
   - Test deployment scenarios

5. **Monitoring**
   - Log important operations
   - Track performance metrics
   - Monitor resource usage
   - Set up alerts for critical events

6. **Deployment**
   - Use rolling updates for zero-downtime deployments
   - Implement health checks
   - Set up rollback procedures
   - Monitor deployment progress

## Related Documentation

- [Base AI Agent](api/base_agent.md)
- [Service Metrics Collector](api/service_metrics_collector.md)
- [Configuration Guide](configuration_guide.md)
- [Troubleshooting Guide](troubleshooting_guide.md)
- [Deployment Guide](deployment_guide.md) 