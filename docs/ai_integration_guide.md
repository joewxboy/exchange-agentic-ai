# AI Integration Guide: Open Horizon with LangChain, LangFlow, and BeeAI

## Table of Contents
1. [LangChain Integration](#1-langchain-integration)
2. [LangFlow Integration](#2-langflow-integration)
3. [BeeAI Integration](#3-beeai-integration)
4. [Best Practices](#4-best-practices)
5. [Example Use Cases](#5-example-use-cases)
6. [MCP Server Integration](#6-mcp-server-integration)
7. [ACP Protocol Integration](#7-acp-protocol-integration)
8. [A2A Protocol Integration](#8-a2a-protocol-integration)
9. [Best Practices for Protocol Integration](#9-best-practices-for-protocol-integration)
10. [Integration Examples](#10-integration-examples)
11. [Configuration Documentation](#11-configuration-documentation)
12. [Using Agentic AI in Jupyter Notebooks](#12-using-agentic-ai-in-jupyter-notebooks)
13. [TypeScript MCP Server Integration](#13-typescript-mcp-server-integration)

This guide explains how to integrate the Open Horizon AI Integration Framework with popular AI orchestration tools.

## 1. LangChain Integration

### 1.1. Basic Integration
```python
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from src.ai.service_agent import ServiceManagementAgent
from src.exchange.client import ExchangeAPIClient

# Initialize Open Horizon components
client = ExchangeAPIClient(
    base_url="http://localhost:8080",
    org="testorg",
    username="user",
    password="pass"
)
service_agent = ServiceManagementAgent(client)

# Create LangChain tools for Open Horizon actions
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
    )
]

# Create a custom prompt template
class OpenHorizonPromptTemplate(StringPromptTemplate):
    template = """You are an AI assistant managing Open Horizon services.
    
    Current state: {state}
    
    Available tools:
    {tools}
    
    Question: {input}
    
    {agent_scratchpad}"""

    def format(self, **kwargs):
        return self.template.format(**kwargs)

# Initialize the agent
prompt = OpenHorizonPromptTemplate()
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

### 1.2. Advanced Integration with Memory
```python
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain

# Add memory to the agent
memory = ConversationBufferMemory()
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True
)

# Use the agent with context
response = agent_executor.run(
    "The service is having high CPU usage. What should we do?",
    memory=memory
)
```

## 2. LangFlow Integration

### 2.1. Creating a Flow
```python
from langflow import load_flow_from_json
from src.ai.metrics import MetricsCollector

# Define the flow in JSON
flow_config = {
    "nodes": [
        {
            "id": "metrics_collector",
            "type": "MetricsCollector",
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
            "source": "metrics_collector",
            "target": "service_agent",
            "type": "metrics_to_agent"
        }
    ]
}

# Load and run the flow
flow = load_flow_from_json(flow_config)
result = flow.run()
```

### 2.2. Custom Node Types
```python
from langflow import CustomNode

class OpenHorizonNode(CustomNode):
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.agent = None

    def build(self, config):
        if self.agent_type == "service":
            self.agent = ServiceManagementAgent(config["client"])
        elif self.agent_type == "node":
            self.agent = NodeManagementAgent(config["client"])
        return self.agent

    def run(self, input_data):
        return self.agent.analyze()
```

## 3. BeeAI Integration

### 3.1. Basic Integration
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

# Use the component
service = OpenHorizonService()
analysis = service.analyze_services()
```

### 3.2. Advanced Integration with Workflows
```python
from beeai import Workflow

# Define a workflow
workflow = Workflow("service_management")

@workflow.step
def collect_metrics():
    collector = MetricsCollector()
    return collector.get_recent_metrics()

@workflow.step
def analyze_metrics(metrics):
    service_agent = ServiceManagementAgent(client)
    return service_agent.analyze_metrics(metrics)

@workflow.step
def take_action(analysis):
    if analysis.get('needs_update'):
        service_agent.act({
            'action': 'update',
            'service_id': analysis['service_id'],
            'update_data': analysis['update_data']
        })

# Run the workflow
workflow.run()
```

## 4. Best Practices

### 4.1. Error Handling
```python
from langchain.tools import BaseTool
from typing import Optional, Type

class SafeOpenHorizonTool(BaseTool):
    name = "openhorizon_tool"
    description = "A safe wrapper for Open Horizon actions"
    
    def _run(self, action: str, **kwargs) -> str:
        try:
            result = self.agent.act({
                'action': action,
                **kwargs
            })
            return f"Success: {result}"
        except Exception as e:
            return f"Error: {str(e)}"
```

### 4.2. State Management
```python
from langchain.memory import RedisMemory

# Use Redis for state management
memory = RedisMemory(
    redis_url="redis://localhost:6379",
    key_prefix="openhorizon:"
)

# Store agent state
memory.save_context(
    {"input": "Check service health"},
    {"output": "Service is healthy"}
)
```

### 4.3. Monitoring and Logging
```python
import logging
from langchain.callbacks import FileCallbackHandler

# Set up logging
handler = FileCallbackHandler("openhorizon_agent.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Use in agent
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    callbacks=[handler],
    verbose=True
)
```

## 5. Example Use Cases

### 5.1. Automated Service Management
```python
# Using LangChain
response = agent_executor.run("""
    Monitor service health for the next hour.
    If CPU usage exceeds 80%, scale the service.
    If memory usage exceeds 85%, restart the service.
""")
```

### 5.2. Intelligent Node Management
```python
# Using BeeAI
@bee.workflow
def node_management():
    node_agent = NodeManagementAgent(client)
    analysis = node_agent.analyze()
    if analysis.get('needs_attention'):
        node_agent.act(analysis['recommended_action'])
```

### 5.3. Metrics Analysis and Prediction
```python
# Using LangFlow
flow_config = {
    "nodes": [
        {
            "id": "collect_metrics",
            "type": "MetricsCollector"
        },
        {
            "id": "analyze_trends",
            "type": "TrendAnalyzer"
        },
        {
            "id": "predict_future",
            "type": "Predictor"
        }
    ]
}
```

## 6. MCP Server Integration

### 6.1. Basic Integration
```python
from src.mcp.client import MCPClient
from src.ai.service_agent import ServiceManagementAgent

class MCPIntegration:
    def __init__(self, server_url: str, credentials: dict):
        self.mcp_client = MCPClient(server_url, credentials)
        self.service_agent = ServiceManagementAgent(self.mcp_client)

    async def connect(self):
        """Establish connection to MCP server"""
        await self.mcp_client.connect()
        return self.mcp_client.is_connected()

    async def monitor_services(self):
        """Monitor services through MCP server"""
        services = await self.mcp_client.get_services()
        for service in services:
            health = await self.service_agent.analyze_health(service)
            if health.needs_action:
                await self.take_action(service, health)

    async def take_action(self, service, health):
        """Take action based on service health"""
        action = health.recommended_action
        await self.mcp_client.execute_action(service.id, action)
```

### 5.2. Advanced Integration with Real-time Monitoring
```python
from src.mcp.monitor import MCPMonitor
from src.ai.analysis import ServiceAnalyzer

class MCPRealTimeMonitor:
    def __init__(self, mcp_client: MCPClient):
        self.monitor = MCPMonitor(mcp_client)
        self.analyzer = ServiceAnalyzer()

    async def start_monitoring(self):
        """Start real-time service monitoring"""
        async for event in self.monitor.subscribe_events():
            if event.type == 'service_health_change':
                analysis = await self.analyzer.analyze_event(event)
                if analysis.requires_action:
                    await self.handle_health_change(event, analysis)

    async def handle_health_change(self, event, analysis):
        """Handle service health changes"""
        action = analysis.recommended_action
        await self.monitor.execute_action(event.service_id, action)
```

## 7. ACP Protocol Integration

### 7.1. Basic Integration
```python
from src.acp.handler import ACPHandler
from src.ai.agent import BaseAIAgent

class ACPIntegration:
    def __init__(self, protocol_version: str = "1.0"):
        self.acp_handler = ACPHandler(protocol_version)
        self.agent = BaseAIAgent()

    async def handle_message(self, message: dict):
        """Handle incoming ACP messages"""
        if message.type == 'service_analysis_request':
            return await self.handle_analysis_request(message)
        elif message.type == 'action_request':
            return await self.handle_action_request(message)

    async def handle_analysis_request(self, message: dict):
        """Handle service analysis requests"""
        analysis = await self.agent.analyze_service(message.service_id)
        return self.acp_handler.format_response('analysis', analysis)

    async def handle_action_request(self, message: dict):
        """Handle action requests"""
        result = await self.agent.execute_action(message.action)
        return self.acp_handler.format_response('action_result', result)
```

### 7.2. Advanced Integration with Protocol Versioning
```python
from src.acp.version import ACPVersionManager
from src.ai.agent import ServiceManagementAgent

class ACPVersionedIntegration:
    def __init__(self):
        self.version_manager = ACPVersionManager()
        self.agent = ServiceManagementAgent()

    async def handle_message(self, message: dict):
        """Handle messages with version support"""
        version = message.get('version', '1.0')
        handler = self.version_manager.get_handler(version)
        
        if handler.supports_message(message):
            return await handler.process_message(message, self.agent)
        else:
            return handler.format_error('unsupported_message_type')
```

## 8. A2A Protocol Integration

### 8.1. Basic Integration
```python
from src.a2a.agent import A2AAgent
from src.ai.agent import BaseAIAgent

class A2AIntegration:
    def __init__(self, agent_id: str):
        self.a2a_agent = A2AAgent(agent_id)
        self.ai_agent = BaseAIAgent()

    async def start(self):
        """Start A2A agent and discover peers"""
        await self.a2a_agent.start()
        peers = await self.a2a_agent.discover_peers()
        for peer in peers:
            await self.setup_peer_communication(peer)

    async def setup_peer_communication(self, peer):
        """Setup communication with a peer agent"""
        await self.a2a_agent.register_peer(peer)
        await self.a2a_agent.subscribe_to_peer(peer, self.handle_peer_message)

    async def handle_peer_message(self, message: dict):
        """Handle messages from peer agents"""
        if message.type == 'service_analysis':
            return await self.handle_analysis_message(message)
        elif message.type == 'action_request':
            return await self.handle_action_message(message)
```

### 8.2. Advanced Integration with Conflict Resolution
```python
from src.a2a.resolver import ConflictResolver
from src.ai.agent import ServiceManagementAgent

class A2AConflictResolution:
    def __init__(self, agent_id: str):
        self.a2a_agent = A2AAgent(agent_id)
        self.resolver = ConflictResolver()
        self.service_agent = ServiceManagementAgent()

    async def handle_conflict(self, conflict: dict):
        """Handle conflicts between agents"""
        resolution = await self.resolver.resolve_conflict(conflict)
        if resolution.requires_action:
            await self.execute_resolution(resolution)

    async def execute_resolution(self, resolution: dict):
        """Execute conflict resolution"""
        if resolution.type == 'service_update':
            await self.service_agent.update_service(
                resolution.service_id,
                resolution.update_data
            )
        elif resolution.type == 'resource_allocation':
            await self.service_agent.allocate_resources(
                resolution.service_id,
                resolution.resources
            )
```

## 9. Best Practices for Protocol Integration

### 9.1. Error Handling and Recovery
```python
from src.common.error import ProtocolError
from src.common.recovery import RecoveryManager

class ProtocolErrorHandler:
    def __init__(self):
        self.recovery_manager = RecoveryManager()

    async def handle_error(self, error: ProtocolError):
        """Handle protocol-specific errors"""
        if error.is_recoverable:
            return await self.recovery_manager.recover(error)
        else:
            return await self.recovery_manager.fail_gracefully(error)
```

### 9.2. Security Considerations
```python
from src.common.security import SecurityManager
from src.common.auth import AuthenticationManager

class ProtocolSecurity:
    def __init__(self):
        self.security_manager = SecurityManager()
        self.auth_manager = AuthenticationManager()

    async def secure_communication(self, message: dict):
        """Secure protocol communication"""
        if not await self.auth_manager.verify_message(message):
            raise SecurityError("Message authentication failed")
        
        return await self.security_manager.encrypt_message(message)
```

### 9.3. Performance Optimization
```python
from src.common.performance import PerformanceMonitor
from src.common.cache import CacheManager

class ProtocolOptimizer:
    def __init__(self):
        self.performance_monitor = PerformanceMonitor()
        self.cache_manager = CacheManager()

    async def optimize_communication(self, message: dict):
        """Optimize protocol communication"""
        if self.cache_manager.has_cached_response(message):
            return self.cache_manager.get_cached_response(message)
        
        result = await self.process_message(message)
        self.cache_manager.cache_response(message, result)
        return result
```

## 10. Integration Examples

### 10.1. Combined Protocol Usage
```python
from src.integration import ProtocolManager

class MultiProtocolIntegration:
    def __init__(self):
        self.protocol_manager = ProtocolManager()
        self.mcp_client = self.protocol_manager.get_mcp_client()
        self.acp_handler = self.protocol_manager.get_acp_handler()
        self.a2a_agent = self.protocol_manager.get_a2a_agent()

    async def start(self):
        """Start all protocol integrations"""
        await self.mcp_client.connect()
        await self.acp_handler.initialize()
        await self.a2a_agent.start()

    async def handle_service_event(self, event: dict):
        """Handle service events across protocols"""
        # MCP monitoring
        if event.source == 'mcp':
            await self.handle_mcp_event(event)
        
        # ACP communication
        elif event.source == 'acp':
            await self.handle_acp_event(event)
        
        # A2A coordination
        elif event.source == 'a2a':
            await self.handle_a2a_event(event)
```

### 10.2. Protocol-specific Error Recovery
```python
from src.recovery import ProtocolRecoveryManager

class ProtocolRecovery:
    def __init__(self):
        self.recovery_manager = ProtocolRecoveryManager()

    async def recover_from_error(self, error: dict):
        """Recover from protocol-specific errors"""
        if error.protocol == 'mcp':
            return await self.recover_mcp_error(error)
        elif error.protocol == 'acp':
            return await self.recover_acp_error(error)
        elif error.protocol == 'a2a':
            return await self.recover_a2a_error(error)
```

## 11. Configuration Documentation

### 11.1. Environment Variables

#### Core Open Horizon Variables
```bash
# Organization and Authentication
HZN_ORG_ID=examples                    # Your Open Horizon organization ID
HZN_EXCHANGE_USER_AUTH=username:password  # Authentication in format username:password
HZN_EXCHANGE_URL=http://open-horizon.lfedge.iol.unh.edu:3090/v1  # Exchange API endpoint
HZN_FSS_CSSURL=http://open-horizon.lfedge.iol.unh.edu:9443/      # File Sync Service URL
HZN_AGBOT_URL=http://open-horizon.lfedge.iol.unh.edu:3111        # Agreement Bot URL
HZN_FDO_SVC_URL=http://open-horizon.lfedge.iol.unh.edu:9008/api  # FDO Service URL

# MCP Server Configuration
MCP_SERVER_URL=http://mcp-server:8080  # MCP server endpoint
MCP_API_KEY=your_api_key              # API key for MCP server authentication
MCP_MONITORING_INTERVAL=30            # Monitoring interval in seconds

# ACP Protocol Configuration
ACP_VERSION=1.0                       # ACP protocol version
ACP_ENCRYPTION_KEY=your_encryption_key # Key for message encryption
ACP_MESSAGE_TIMEOUT=60                # Message timeout in seconds

# A2A Protocol Configuration
A2A_AGENT_ID=agent_001                # Unique identifier for this agent
A2A_DISCOVERY_INTERVAL=300            # Peer discovery interval in seconds
A2A_PEER_TIMEOUT=180                  # Peer timeout in seconds
```

#### Environment Variable Validation
```python
from typing import Dict, Optional
import os
import re
from urllib.parse import urlparse

class EnvironmentValidator:
    def __init__(self):
        self.required_vars = {
            'HZN_ORG_ID': self._validate_org_id,
            'HZN_EXCHANGE_USER_AUTH': self._validate_auth,
            'HZN_EXCHANGE_URL': self._validate_url,
            'HZN_FSS_CSSURL': self._validate_url,
            'HZN_AGBOT_URL': self._validate_url,
            'HZN_FDO_SVC_URL': self._validate_url
        }
        
        self.optional_vars = {
            'MCP_SERVER_URL': self._validate_url,
            'MCP_API_KEY': self._validate_api_key,
            'MCP_MONITORING_INTERVAL': self._validate_interval,
            'ACP_VERSION': self._validate_version,
            'ACP_ENCRYPTION_KEY': self._validate_encryption_key,
            'ACP_MESSAGE_TIMEOUT': self._validate_timeout,
            'A2A_AGENT_ID': self._validate_agent_id,
            'A2A_DISCOVERY_INTERVAL': self._validate_interval,
            'A2A_PEER_TIMEOUT': self._validate_timeout
        }

    def validate_all(self) -> Dict[str, Optional[str]]:
        """Validate all environment variables"""
        errors = {}
        
        # Check required variables
        for var, validator in self.required_vars.items():
            value = os.getenv(var)
            if not value:
                errors[var] = f"Required environment variable {var} is not set"
            else:
                error = validator(value)
                if error:
                    errors[var] = error
        
        # Check optional variables
        for var, validator in self.optional_vars.items():
            value = os.getenv(var)
            if value:
                error = validator(value)
                if error:
                    errors[var] = error
        
        return errors

    def _validate_org_id(self, value: str) -> Optional[str]:
        """Validate organization ID format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            return "Organization ID must contain only alphanumeric characters, underscores, and hyphens"
        return None

    def _validate_auth(self, value: str) -> Optional[str]:
        """Validate authentication format"""
        if not re.match(r'^[^:]+:[^:]+$', value):
            return "Authentication must be in format username:password"
        return None

    def _validate_url(self, value: str) -> Optional[str]:
        """Validate URL format"""
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                return "Invalid URL format"
        except:
            return "Invalid URL format"
        return None

    def _validate_api_key(self, value: str) -> Optional[str]:
        """Validate API key format"""
        if len(value) < 32:
            return "API key must be at least 32 characters long"
        return None

    def _validate_interval(self, value: str) -> Optional[str]:
        """Validate interval value"""
        try:
            interval = int(value)
            if interval < 1:
                return "Interval must be greater than 0"
        except ValueError:
            return "Interval must be a valid integer"
        return None

    def _validate_version(self, value: str) -> Optional[str]:
        """Validate version format"""
        if not re.match(r'^\d+\.\d+(\.\d+)?$', value):
            return "Version must be in format x.y or x.y.z"
        return None

    def _validate_encryption_key(self, value: str) -> Optional[str]:
        """Validate encryption key format"""
        if len(value) < 32:
            return "Encryption key must be at least 32 characters long"
        return None

    def _validate_timeout(self, value: str) -> Optional[str]:
        """Validate timeout value"""
        try:
            timeout = int(value)
            if timeout < 1:
                return "Timeout must be greater than 0"
        except ValueError:
            return "Timeout must be a valid integer"
        return None

    def _validate_agent_id(self, value: str) -> Optional[str]:
        """Validate agent ID format"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', value):
            return "Agent ID must contain only alphanumeric characters, underscores, and hyphens"
        return None
```

#### Usage Examples

1. **Initializing the Exchange Client**
```python
from src.exchange.client import ExchangeAPIClient
import os

def create_exchange_client():
    """Create and configure Exchange API client"""
    org_id = os.getenv('HZN_ORG_ID')
    auth = os.getenv('HZN_EXCHANGE_USER_AUTH')
    exchange_url = os.getenv('HZN_EXCHANGE_URL')
    
    if not all([org_id, auth, exchange_url]):
        raise ValueError("Missing required environment variables")
    
    username, password = auth.split(':')
    return ExchangeAPIClient(
        base_url=exchange_url,
        org=org_id,
        username=username,
        password=password
    )
```

2. **Configuring MCP Integration**
```python
from src.mcp.client import MCPClient
import os

def create_mcp_client():
    """Create and configure MCP client"""
    server_url = os.getenv('MCP_SERVER_URL')
    api_key = os.getenv('MCP_API_KEY')
    interval = int(os.getenv('MCP_MONITORING_INTERVAL', '30'))
    
    if not all([server_url, api_key]):
        raise ValueError("Missing required MCP configuration")
    
    return MCPClient(
        server_url=server_url,
        api_key=api_key,
        monitoring_interval=interval
    )
```

3. **Setting up ACP Protocol**
```python
from src.acp.handler import ACPHandler
import os

def create_acp_handler():
    """Create and configure ACP handler"""
    version = os.getenv('ACP_VERSION', '1.0')
    encryption_key = os.getenv('ACP_ENCRYPTION_KEY')
    timeout = int(os.getenv('ACP_MESSAGE_TIMEOUT', '60'))
    
    if not encryption_key:
        raise ValueError("Missing ACP encryption key")
    
    return ACPHandler(
        version=version,
        encryption_key=encryption_key,
        message_timeout=timeout
    )
```

4. **Initializing A2A Agent**
```python
from src.a2a.agent import A2AAgent
import os

def create_a2a_agent():
    """Create and configure A2A agent"""
    agent_id = os.getenv('A2A_AGENT_ID')
    discovery_interval = int(os.getenv('A2A_DISCOVERY_INTERVAL', '300'))
    peer_timeout = int(os.getenv('A2A_PEER_TIMEOUT', '180'))
    
    if not agent_id:
        raise ValueError("Missing A2A agent ID")
    
    return A2AAgent(
        agent_id=agent_id,
        discovery_interval=discovery_interval,
        peer_timeout=peer_timeout
    )
```

5. **Environment Validation Script**
```python
#!/usr/bin/env python3
from src.config.validator import EnvironmentValidator
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_environment():
    """Validate all environment variables"""
    validator = EnvironmentValidator()
    errors = validator.validate_all()
    
    if errors:
        logger.error("Environment validation failed:")
        for var, error in errors.items():
            logger.error(f"  {var}: {error}")
        sys.exit(1)
    
    logger.info("Environment validation successful")

if __name__ == "__main__":
    validate_environment()
```

Note: Replace the example values with your actual configuration. The URLs should be updated to match your Open Horizon deployment, and sensitive values like API keys and encryption keys should be properly secured.

### 11.2. Configuration Files

#### MCP Server Configuration
```yaml
# mcp_config.yaml
server:
  url: http://mcp-server:8080
  api_key: your_api_key
  timeout: 30
  retry_attempts: 3

monitoring:
  interval: 30
  metrics:
    - cpu_usage
    - memory_usage
    - response_time
  thresholds:
    cpu_usage: 80
    memory_usage: 85
    response_time: 1000

security:
  encryption: true
  ssl_verify: true
  allowed_ips:
    - 192.168.1.0/24
```

#### ACP Protocol Configuration
```yaml
# acp_config.yaml
protocol:
  version: "1.0"
  encryption_key: your_encryption_key
  message_timeout: 60

handlers:
  service_analysis:
    enabled: true
    timeout: 30
    retry_attempts: 3
  action_request:
    enabled: true
    timeout: 60
    retry_attempts: 5

security:
  authentication:
    type: "api_key"
    key: your_auth_key
  encryption:
    algorithm: "AES-256-GCM"
    key_rotation: 86400
```

#### A2A Protocol Configuration
```yaml
# a2a_config.yaml
agent:
  id: agent_001
  name: "Service Management Agent"
  capabilities:
    - service_analysis
    - action_execution
    - conflict_resolution

discovery:
  interval: 300
  timeout: 180
  max_peers: 10

communication:
  encryption: true
  compression: true
  max_message_size: 1048576

conflict_resolution:
  strategy: "consensus"
  timeout: 60
  max_attempts: 3
```

### 11.3. Configuration Validation

```python
from src.config.validator import ConfigValidator
from src.config.exceptions import ConfigurationError

class ProtocolConfigValidator:
    def __init__(self):
        self.validator = ConfigValidator()

    def validate_mcp_config(self, config: dict) -> bool:
        """Validate MCP server configuration"""
        required_fields = ['server', 'monitoring', 'security']
        if not self.validator.validate_structure(config, required_fields):
            raise ConfigurationError("Missing required MCP configuration fields")

        # Validate server configuration
        server_config = config['server']
        if not self.validator.validate_url(server_config['url']):
            raise ConfigurationError("Invalid MCP server URL")

        # Validate monitoring configuration
        monitoring_config = config['monitoring']
        if not self.validator.validate_metrics(monitoring_config['metrics']):
            raise ConfigurationError("Invalid monitoring metrics")

        return True

    def validate_acp_config(self, config: dict) -> bool:
        """Validate ACP protocol configuration"""
        required_fields = ['protocol', 'handlers', 'security']
        if not self.validator.validate_structure(config, required_fields):
            raise ConfigurationError("Missing required ACP configuration fields")

        # Validate protocol version
        if not self.validator.validate_version(config['protocol']['version']):
            raise ConfigurationError("Invalid ACP protocol version")

        # Validate security configuration
        security_config = config['security']
        if not self.validator.validate_security_config(security_config):
            raise ConfigurationError("Invalid security configuration")

        return True

    def validate_a2a_config(self, config: dict) -> bool:
        """Validate A2A protocol configuration"""
        required_fields = ['agent', 'discovery', 'communication']
        if not self.validator.validate_structure(config, required_fields):
            raise ConfigurationError("Missing required A2A configuration fields")

        # Validate agent configuration
        agent_config = config['agent']
        if not self.validator.validate_agent_config(agent_config):
            raise ConfigurationError("Invalid agent configuration")

        # Validate discovery configuration
        discovery_config = config['discovery']
        if not self.validator.validate_discovery_config(discovery_config):
            raise ConfigurationError("Invalid discovery configuration")

        return True
```

### 11.4. Configuration Loading

```python
from src.config.loader import ConfigLoader
from src.config.validator import ProtocolConfigValidator

class ProtocolConfigManager:
    def __init__(self):
        self.loader = ConfigLoader()
        self.validator = ProtocolConfigValidator()

    def load_configurations(self) -> dict:
        """Load and validate all protocol configurations"""
        configs = {
            'mcp': self.load_mcp_config(),
            'acp': self.load_acp_config(),
            'a2a': self.load_a2a_config()
        }
        return configs

    def load_mcp_config(self) -> dict:
        """Load and validate MCP configuration"""
        config = self.loader.load_yaml('mcp_config.yaml')
        self.validator.validate_mcp_config(config)
        return config

    def load_acp_config(self) -> dict:
        """Load and validate ACP configuration"""
        config = self.loader.load_yaml('acp_config.yaml')
        self.validator.validate_acp_config(config)
        return config

    def load_a2a_config(self) -> dict:
        """Load and validate A2A configuration"""
        config = self.loader.load_yaml('a2a_config.yaml')
        self.validator.validate_a2a_config(config)
        return config
```

### 11.5. Configuration Troubleshooting

#### Common Configuration Issues

1. **MCP Server Connection Issues**
   ```python
   # Check MCP server connection
   async def verify_mcp_connection(config: dict) -> bool:
       try:
           client = MCPClient(config['server']['url'])
           await client.connect()
           return client.is_connected()
       except ConnectionError as e:
           logger.error(f"MCP connection failed: {str(e)}")
           return False
   ```

2. **ACP Protocol Version Mismatch**
   ```python
   # Verify ACP protocol version compatibility
   def verify_acp_version(config: dict) -> bool:
       current_version = config['protocol']['version']
       supported_versions = ['1.0', '1.1']
       if current_version not in supported_versions:
           logger.error(f"Unsupported ACP version: {current_version}")
           return False
       return True
   ```

3. **A2A Agent Discovery Issues**
   ```python
   # Troubleshoot A2A agent discovery
   async def troubleshoot_discovery(config: dict) -> dict:
       issues = []
       if config['discovery']['interval'] < 60:
           issues.append("Discovery interval too short")
       if config['discovery']['timeout'] > 300:
           issues.append("Discovery timeout too long")
       return {'has_issues': len(issues) > 0, 'issues': issues}
   ```

#### Configuration Validation Script
```python
#!/usr/bin/env python3
from src.config.manager import ProtocolConfigManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def validate_configurations():
    """Validate all protocol configurations"""
    manager = ProtocolConfigManager()
    try:
        configs = manager.load_configurations()
        logger.info("All configurations validated successfully")
        return True
    except ConfigurationError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        return False

if __name__ == "__main__":
    validate_configurations()
```

### 11.6. Best Practices

1. **Configuration Management**
   - Use environment variables for sensitive data
   - Keep configuration files in version control
   - Use configuration validation
   - Implement configuration reloading
   - Document all configuration options

2. **Security Considerations**
   - Encrypt sensitive configuration data
   - Use secure storage for credentials
   - Implement access control
   - Regular security audits
   - Rotate encryption keys

3. **Performance Optimization**
   - Cache configuration values
   - Minimize configuration reloads
   - Use efficient validation
   - Implement lazy loading
   - Monitor configuration impact

4. **Maintenance**
   - Regular configuration reviews
   - Update documentation
   - Monitor configuration changes
   - Backup configurations
   - Test configuration changes

For more detailed information about specific configuration options, refer to the API documentation in `docs/api/`.

## 12. Using Agentic AI in Jupyter Notebooks

### 12.1. Local Development Setup

First, create a new virtual environment and install the required packages:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install jupyter
pip install openhorizon-agentic-ai
pip install langchain
pip install pandas
pip install matplotlib
```

### 12.2. Basic Notebook Example

Create a new file `openhorizon_analysis.ipynb` with the following cells:

```python
# Cell 1: Import required modules
import os
from src.exchange.client import ExchangeAPIClient
from src.ai.service_agent import ServiceManagementAgent
from src.ai.metrics import MetricsCollector
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib inline

# Cell 2: Configure environment variables
os.environ['HZN_ORG_ID'] = 'examples'
os.environ['HZN_EXCHANGE_USER_AUTH'] = 'your_username:your_password'
os.environ['HZN_EXCHANGE_URL'] = 'http://localhost:8080/v1'

# Cell 3: Initialize clients and agents
client = ExchangeAPIClient(
    base_url=os.getenv('HZN_EXCHANGE_URL'),
    org=os.getenv('HZN_ORG_ID'),
    username=os.getenv('HZN_EXCHANGE_USER_AUTH').split(':')[0],
    password=os.getenv('HZN_EXCHANGE_USER_AUTH').split(':')[1]
)

service_agent = ServiceManagementAgent(client)
metrics_collector = MetricsCollector(client)

# Cell 4: Collect and analyze service metrics
services = client.list_services()
metrics_data = []

for service in services:
    metrics = metrics_collector.collect_service_metrics(service['id'])
    metrics_data.append({
        'service_id': service['id'],
        'cpu_usage': metrics['cpu_usage'],
        'memory_usage': metrics['memory_usage'],
        'response_time': metrics['response_time']
    })

# Convert to DataFrame for analysis
df = pd.DataFrame(metrics_data)
df.head()

# Cell 5: Visualize metrics
plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
df.boxplot(column=['cpu_usage', 'memory_usage'])
plt.title('Resource Usage Distribution')

plt.subplot(1, 2, 2)
plt.scatter(df['cpu_usage'], df['memory_usage'])
plt.xlabel('CPU Usage (%)')
plt.ylabel('Memory Usage (%)')
plt.title('CPU vs Memory Usage')
plt.show()

# Cell 6: Get AI recommendations
recommendations = []
for service in services:
    analysis = service_agent.analyze_service(service['id'])
    recommendations.append({
        'service_id': service['id'],
        'health_status': analysis['health_status'],
        'recommendations': analysis['recommendations']
    })

# Display recommendations
pd.DataFrame(recommendations)
```

### 12.3. Advanced Analysis Example

Create another notebook `advanced_analysis.ipynb` for more complex analysis:

```python
# Cell 1: Import additional modules
from src.ai.trend_analyzer import TrendAnalyzer
from src.ai.predictor import ServicePredictor
import seaborn as sns
from datetime import datetime, timedelta

# Cell 2: Initialize advanced components
trend_analyzer = TrendAnalyzer()
predictor = ServicePredictor()

# Cell 3: Collect historical data
end_time = datetime.now()
start_time = end_time - timedelta(days=7)
historical_data = metrics_collector.collect_historical_metrics(
    start_time=start_time,
    end_time=end_time
)

# Cell 4: Analyze trends
trends = trend_analyzer.analyze_trends(historical_data)
trend_df = pd.DataFrame(trends)

# Cell 5: Visualize trends
plt.figure(figsize=(15, 10))

# CPU Usage Trend
plt.subplot(2, 2, 1)
sns.lineplot(data=trend_df, x='timestamp', y='cpu_usage', hue='service_id')
plt.title('CPU Usage Trend')
plt.xticks(rotation=45)

# Memory Usage Trend
plt.subplot(2, 2, 2)
sns.lineplot(data=trend_df, x='timestamp', y='memory_usage', hue='service_id')
plt.title('Memory Usage Trend')
plt.xticks(rotation=45)

# Response Time Trend
plt.subplot(2, 2, 3)
sns.lineplot(data=trend_df, x='timestamp', y='response_time', hue='service_id')
plt.title('Response Time Trend')
plt.xticks(rotation=45)

# Error Rate Trend
plt.subplot(2, 2, 4)
sns.lineplot(data=trend_df, x='timestamp', y='error_rate', hue='service_id')
plt.title('Error Rate Trend')
plt.xticks(rotation=45)

plt.tight_layout()
plt.show()

# Cell 6: Make predictions
predictions = predictor.predict_service_metrics(
    historical_data=historical_data,
    prediction_horizon=timedelta(hours=24)
)

# Cell 7: Visualize predictions
plt.figure(figsize=(12, 6))
for service_id in predictions['service_id'].unique():
    service_data = predictions[predictions['service_id'] == service_id]
    plt.plot(service_data['timestamp'], service_data['predicted_cpu'], 
             label=f'Service {service_id} (Predicted)')
    plt.fill_between(service_data['timestamp'],
                    service_data['predicted_cpu_lower'],
                    service_data['predicted_cpu_upper'],
                    alpha=0.2)

plt.title('CPU Usage Predictions')
plt.xlabel('Time')
plt.ylabel('CPU Usage (%)')
plt.legend()
plt.show()

# Cell 8: Generate recommendations
recommendations = service_agent.generate_recommendations(
    historical_data=historical_data,
    predictions=predictions
)

# Display recommendations in a formatted table
pd.DataFrame(recommendations).style.set_properties(**{
    'background-color': 'lightyellow',
    'color': 'black',
    'border-color': 'black',
    'border-style': 'solid',
    'border-width': '1px'
})
```

### 12.4. Interactive Dashboard Example

Create a notebook `interactive_dashboard.ipynb` for real-time monitoring:

```python
# Cell 1: Import interactive components
import ipywidgets as widgets
from IPython.display import display, clear_output
import asyncio
from datetime import datetime

# Cell 2: Create dashboard widgets
service_selector = widgets.Dropdown(
    options=[s['id'] for s in services],
    description='Service:'
)

metric_selector = widgets.Dropdown(
    options=['cpu_usage', 'memory_usage', 'response_time', 'error_rate'],
    description='Metric:'
)

time_range = widgets.Dropdown(
    options=['1h', '6h', '12h', '24h'],
    description='Time Range:'
)

update_button = widgets.Button(description='Update Dashboard')
output = widgets.Output()

# Cell 3: Define update function
async def update_dashboard(button):
    with output:
        clear_output()
        service_id = service_selector.value
        metric = metric_selector.value
        range_hours = int(time_range.value[:-1])
        
        # Collect data
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=range_hours)
        data = metrics_collector.collect_historical_metrics(
            service_id=service_id,
            start_time=start_time,
            end_time=end_time
        )
        
        # Create visualization
        plt.figure(figsize=(12, 6))
        plt.plot(data['timestamp'], data[metric])
        plt.title(f'{metric.replace("_", " ").title()} for Service {service_id}')
        plt.xlabel('Time')
        plt.ylabel(metric.replace('_', ' ').title())
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        # Display current recommendations
        analysis = service_agent.analyze_service(service_id)
        print("\nCurrent Recommendations:")
        for rec in analysis['recommendations']:
            print(f"- {rec}")

# Cell 4: Set up dashboard
update_button.on_click(update_dashboard)
dashboard = widgets.VBox([
    widgets.HBox([service_selector, metric_selector, time_range]),
    update_button,
    output
])

# Cell 5: Display dashboard
display(dashboard)
```

### 12.5. Best Practices for Notebook Development

1. **Environment Management**
   - Use virtual environments for isolation
   - Document package versions in requirements.txt
   - Use environment variables for configuration

2. **Code Organization**
   - Split complex analysis into multiple notebooks
   - Use markdown cells for documentation
   - Create reusable functions for common tasks

3. **Performance Optimization**
   - Cache expensive computations
   - Use async/await for I/O operations
   - Implement proper error handling

4. **Visualization**
   - Use appropriate chart types
   - Include proper labels and titles
   - Add interactive elements when useful

5. **Security**
   - Never commit credentials to notebooks
   - Use environment variables for sensitive data
   - Implement proper access controls

For more examples and detailed documentation, refer to the API documentation in `docs/api/`.

## 13. TypeScript MCP Server Integration

### 13.1. Project Setup

First, create a new TypeScript project and install the required dependencies:

```bash
# Create new project
mkdir mcp-agentic-server
cd mcp-agentic-server
npm init -y

# Install dependencies
npm install typescript @types/node ts-node
npm install express @types/express
npm install axios
npm install dotenv
npm install openhorizon-agentic-ai
npm install @types/ws ws
npm install winston

# Initialize TypeScript
npx tsc --init
```

### 13.2. Basic MCP Server Implementation

Create the following files:

```typescript
// src/types/index.ts
export interface ServiceMetrics {
  serviceId: string;
  cpuUsage: number;
  memoryUsage: number;
  responseTime: number;
  errorRate: number;
  timestamp: Date;
}

export interface ServiceAnalysis {
  serviceId: string;
  healthStatus: 'healthy' | 'warning' | 'critical';
  recommendations: string[];
  metrics: ServiceMetrics;
}

export interface MCPConfig {
  port: number;
  exchangeUrl: string;
  orgId: string;
  auth: string;
}
```

```typescript
// src/config/config.ts
import dotenv from 'dotenv';
import { MCPConfig } from '../types';

dotenv.config();

export const config: MCPConfig = {
  port: parseInt(process.env.MCP_PORT || '8080'),
  exchangeUrl: process.env.HZN_EXCHANGE_URL || '',
  orgId: process.env.HZN_ORG_ID || '',
  auth: process.env.HZN_EXCHANGE_USER_AUTH || ''
};

export const validateConfig = (): void => {
  const required = ['exchangeUrl', 'orgId', 'auth'];
  const missing = required.filter(key => !config[key as keyof MCPConfig]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required configuration: ${missing.join(', ')}`);
  }
};
```

```typescript
// src/services/agenticService.ts
import { ServiceAnalysis, ServiceMetrics } from '../types';
import { ServiceManagementAgent, MetricsCollector } from 'openhorizon-agentic-ai';
import { ExchangeAPIClient } from 'openhorizon-agentic-ai';
import { config } from '../config/config';

export class AgenticService {
  private client: ExchangeAPIClient;
  private serviceAgent: ServiceManagementAgent;
  private metricsCollector: MetricsCollector;

  constructor() {
    const [username, password] = config.auth.split(':');
    this.client = new ExchangeAPIClient({
      baseUrl: config.exchangeUrl,
      org: config.orgId,
      username,
      password
    });
    
    this.serviceAgent = new ServiceManagementAgent(this.client);
    this.metricsCollector = new MetricsCollector(this.client);
  }

  async analyzeService(serviceId: string): Promise<ServiceAnalysis> {
    try {
      const metrics = await this.metricsCollector.collectServiceMetrics(serviceId);
      const analysis = await this.serviceAgent.analyzeService(serviceId);
      
      return {
        serviceId,
        healthStatus: analysis.healthStatus,
        recommendations: analysis.recommendations,
        metrics: {
          serviceId,
          cpuUsage: metrics.cpuUsage,
          memoryUsage: metrics.memoryUsage,
          responseTime: metrics.responseTime,
          errorRate: metrics.errorRate,
          timestamp: new Date()
        }
      };
    } catch (error) {
      console.error(`Error analyzing service ${serviceId}:`, error);
      throw error;
    }
  }

  async getServiceMetrics(serviceId: string): Promise<ServiceMetrics> {
    try {
      const metrics = await this.metricsCollector.collectServiceMetrics(serviceId);
      return {
        serviceId,
        ...metrics,
        timestamp: new Date()
      };
    } catch (error) {
      console.error(`Error getting metrics for service ${serviceId}:`, error);
      throw error;
    }
  }
}
```

```typescript
// src/server.ts
import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';
import { AgenticService } from './services/agenticService';
import { config, validateConfig } from './config/config';
import winston from 'winston';

// Configure logger
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

// Initialize Express app
const app = express();
app.use(express.json());

// Initialize Agentic service
const agenticService = new AgenticService();

// Create HTTP server
const server = createServer(app);

// Create WebSocket server
const wss = new WebSocketServer({ server });

// WebSocket connection handler
wss.on('connection', (ws) => {
  logger.info('New WebSocket connection established');

  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message.toString());
      
      if (data.type === 'analyze_service') {
        const analysis = await agenticService.analyzeService(data.serviceId);
        ws.send(JSON.stringify({
          type: 'analysis_result',
          data: analysis
        }));
      }
    } catch (error) {
      logger.error('Error processing WebSocket message:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: 'Error processing request'
      }));
    }
  });
});

// REST API endpoints
app.get('/api/services/:serviceId/analysis', async (req, res) => {
  try {
    const analysis = await agenticService.analyzeService(req.params.serviceId);
    res.json(analysis);
  } catch (error) {
    logger.error('Error in /api/services/:serviceId/analysis:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/services/:serviceId/metrics', async (req, res) => {
  try {
    const metrics = await agenticService.getServiceMetrics(req.params.serviceId);
    res.json(metrics);
  } catch (error) {
    logger.error('Error in /api/services/:serviceId/metrics:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Start server
const startServer = async () => {
  try {
    validateConfig();
    server.listen(config.port, () => {
      logger.info(`MCP server listening on port ${config.port}`);
    });
  } catch (error) {
    logger.error('Failed to start server:', error);
    process.exit(1);
  }
};

startServer();
```

### 13.3. Client Example

Create a TypeScript client to interact with the MCP server:

```typescript
// src/client/mcpClient.ts
import WebSocket from 'ws';
import axios from 'axios';
import { ServiceAnalysis, ServiceMetrics } from '../types';

export class MCPClient {
  private ws: WebSocket;
  private baseUrl: string;

  constructor(serverUrl: string) {
    this.baseUrl = serverUrl;
    this.ws = new WebSocket(serverUrl);
    this.setupWebSocket();
  }

  private setupWebSocket() {
    this.ws.on('open', () => {
      console.log('Connected to MCP server');
    });

    this.ws.on('message', (data) => {
      const message = JSON.parse(data.toString());
      this.handleMessage(message);
    });

    this.ws.on('error', (error) => {
      console.error('WebSocket error:', error);
    });

    this.ws.on('close', () => {
      console.log('Disconnected from MCP server');
    });
  }

  private handleMessage(message: any) {
    switch (message.type) {
      case 'analysis_result':
        this.handleAnalysisResult(message.data);
        break;
      case 'error':
        console.error('Server error:', message.message);
        break;
    }
  }

  private handleAnalysisResult(analysis: ServiceAnalysis) {
    console.log('Received service analysis:', analysis);
    // Implement your analysis handling logic here
  }

  async requestServiceAnalysis(serviceId: string): Promise<void> {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'analyze_service',
        serviceId
      }));
    } else {
      throw new Error('WebSocket is not connected');
    }
  }

  async getServiceAnalysis(serviceId: string): Promise<ServiceAnalysis> {
    const response = await axios.get(`${this.baseUrl}/api/services/${serviceId}/analysis`);
    return response.data;
  }

  async getServiceMetrics(serviceId: string): Promise<ServiceMetrics> {
    const response = await axios.get(`${this.baseUrl}/api/services/${serviceId}/metrics`);
    return response.data;
  }
}
```

### 13.4. Usage Example

```typescript
// src/example.ts
import { MCPClient } from './client/mcpClient';

async function main() {
  const client = new MCPClient('ws://localhost:8080');

  // Request real-time analysis
  await client.requestServiceAnalysis('service-1');

  // Get analysis via REST API
  const analysis = await client.getServiceAnalysis('service-1');
  console.log('Service analysis:', analysis);

  // Get metrics via REST API
  const metrics = await client.getServiceMetrics('service-1');
  console.log('Service metrics:', metrics);
}

main().catch(console.error);
```

### 13.5. Best Practices

1. **Error Handling**
   - Implement comprehensive error handling
   - Use TypeScript's type system for error types
   - Log errors with appropriate context
   - Implement retry mechanisms for transient failures

2. **Security**
   - Use environment variables for sensitive data
   - Implement proper authentication
   - Use HTTPS/WSS for production
   - Validate all input data

3. **Performance**
   - Implement connection pooling
   - Use WebSocket for real-time updates
   - Cache frequently accessed data
   - Implement rate limiting

4. **Monitoring**
   - Log important events
   - Track performance metrics
   - Monitor WebSocket connections
   - Implement health checks

5. **Testing**
   - Write unit tests for business logic
   - Implement integration tests
   - Test WebSocket communication
   - Test error scenarios

For more detailed information about the MCP server implementation, refer to the API documentation in `docs/api/`. 