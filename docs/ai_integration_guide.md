# AI Integration Guide: Open Horizon with LangChain, LangFlow, and BeeAI

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

---
For more details, see the API documentation in `docs/api/` and usage examples in `docs/usage_examples.md`. 