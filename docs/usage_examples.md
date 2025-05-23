# Usage Examples: Open Horizon AI Integration Framework

This guide provides practical examples for using the core components of the Open Horizon AI Integration Framework, including metrics collectors and AI agents.

For detailed API documentation, see:
- [Base AI Agent](api/base_agent.md)
- [Service Management Agent](api/service_agent.md)
- [Node Management Agent](api/node_agent.md)
- [Metrics Collector](api/metrics_collector.md)
- [Service Metrics Collector](api/service_metrics_collector.md)
- [Node Metrics Collector](api/node_metrics_collector.md)

For configuration details, see the [Configuration Guide](configuration_guide.md).

## 1. Metrics Collectors

### 1.1. Basic Metrics Collection
```python
from src.ai.metrics import MetricsCollector
from datetime import timedelta

collector = MetricsCollector(analysis_window=timedelta(minutes=30))
collector.add_metrics({'cpu_usage': 75.5, 'memory_usage': 82.3, 'error_rate': 0.02})
recent_metrics = collector.get_recent_metrics(timedelta(minutes=15))
analysis = collector.analyze_metrics(recent_metrics)
print(analysis)
```

### 1.2. Service Metrics Collector
```python
from src.ai.service_metrics import ServiceMetricsCollector

service_collector = ServiceMetricsCollector()
service_collector.add_metrics({'cpu_usage': 60.0, 'memory_usage': 70.0, 'error_rate': 0.01, 'response_time': 200})
service_analysis = service_collector.analyze_metrics(service_collector.get_recent_metrics())
print(service_analysis)
```

### 1.3. Node Metrics Collector
```python
from src.ai.node_metrics import NodeMetricsCollector

node_collector = NodeMetricsCollector()
node_collector.add_metrics({'cpu_usage': 50.0, 'memory_usage': 65.0, 'disk_usage': 80.0, 'temperature': 70.0})
node_analysis = node_collector.analyze_metrics(node_collector.get_recent_metrics())
print(node_analysis)
```

## 2. AI Agents

### 2.1. Service Management Agent
```python
from src.exchange.client import ExchangeAPIClient
from src.ai.service_agent import ServiceManagementAgent

client = ExchangeAPIClient(base_url="http://localhost:8080", org="testorg", username="user", password="pass")
service_agent = ServiceManagementAgent(client)

# Analyze all services and get recommendations
analysis = service_agent.analyze()
print(analysis)

# Act on a recommendation (e.g., update a service)
service_agent.act({'action': 'update', 'service_id': 'my-service', 'update_data': {"version": "2.0.0"}})
```

### 2.2. Node Management Agent
```python
from src.exchange.client import ExchangeAPIClient
from src.ai.node_agent import NodeManagementAgent

client = ExchangeAPIClient(base_url="http://localhost:8080", org="testorg", username="user", password="pass")
node_agent = NodeManagementAgent(client)

# Analyze all nodes and get recommendations
analysis = node_agent.analyze()
print(analysis)

# Act on a recommendation (e.g., update a node)
node_agent.act({'action': 'update', 'node_id': 'node-1', 'update_data': {"name": "new-node-name"}})
```

## 3. Alert Handling

```python
# After analysis, check for alerts
alerts = analysis.get('alerts', [])
for alert in alerts:
    print(f"ALERT: {alert['message']}")
```

## 4. Advanced Usage

### 4.1. Custom Analysis Window
```python
from datetime import timedelta
collector = MetricsCollector(analysis_window=timedelta(hours=2))
```

### 4.2. Concurrent Metrics Collection
```python
import asyncio
async def collect_metrics(collector, metrics, n):
    for _ in range(n):
        collector.add_metrics(metrics)
        await asyncio.sleep(0)
# Usage: asyncio.run(collect_metrics(collector, {'cpu_usage': 50}, 1000))
```

### 4.3. Custom Alert Thresholds and Actions
```python
import os
os.environ['SERVICE_CPU_THRESHOLD'] = '70'  # Lower threshold for testing
from src.ai.service_metrics import ServiceMetricsCollector
service_collector = ServiceMetricsCollector()
service_collector.add_metrics({'cpu_usage': 75.0})
alerts = service_collector.analyze_metrics(service_collector.get_recent_metrics())['alerts']
for alert in alerts:
    if alert['type'] == 'critical':
        print(f"CRITICAL ALERT: {alert['message']}")
        # Custom action: send notification, trigger auto-scaling, etc.
```

### 4.4. Using Multiple Agents Together
```python
from src.exchange.client import ExchangeAPIClient
from src.ai.service_agent import ServiceManagementAgent
from src.ai.node_agent import NodeManagementAgent

client = ExchangeAPIClient(base_url="http://localhost:8080", org="testorg", username="user", password="pass")
service_agent = ServiceManagementAgent(client)
node_agent = NodeManagementAgent(client)

# Analyze and act on both services and nodes
service_analysis = service_agent.analyze()
node_analysis = node_agent.analyze()
# Respond to recommendations from both
for rec in service_analysis.get('recommendations', []):
    service_agent.act(rec)
for rec in node_analysis.get('recommendations', []):
    node_agent.act(rec)
```

### 4.5. Dynamic Configuration at Runtime
```python
from src.ai.metrics import MetricsCollector
collector = MetricsCollector()
# Change analysis window on the fly
collector._analysis_window = timedelta(minutes=10)
```

### 4.6. Integration with External Monitoring/Logging
```python
import logging
logging.basicConfig(level=logging.INFO)
from src.ai.metrics import MetricsCollector
collector = MetricsCollector()
collector.add_metrics({'cpu_usage': 90.0})
analysis = collector.analyze_metrics(collector.get_recent_metrics())
for alert in analysis['alerts']:
    logging.info(f"ALERT: {alert['message']}")
    # Optionally, send to external system (e.g., Prometheus, Grafana, Slack)
```

### 4.7. Collecting and Analyzing Real API Data
```python
from src.exchange.client import ExchangeAPIClient
from src.ai.service_metrics import ServiceMetricsCollector
client = ExchangeAPIClient(base_url="http://localhost:8080", org="testorg", username="user", password="pass")
service_collector = ServiceMetricsCollector()
services = client.list_services("testorg")
for service in services:
    metrics = service.get('metrics', {})
    service_collector.add_metrics(metrics)
analysis = service_collector.analyze_metrics(service_collector.get_recent_metrics())
print(analysis)
```

### 4.8. Programmatic Response to Critical Alerts
```python
from src.ai.node_metrics import NodeMetricsCollector
node_collector = NodeMetricsCollector()
node_collector.add_metrics({'cpu_usage': 99.0, 'temperature': 85.0})
analysis = node_collector.analyze_metrics(node_collector.get_recent_metrics())
for alert in analysis['alerts']:
    if alert['type'] == 'critical':
        # Take automated action, e.g., shut down node, notify admin
        print(f"Automated response to: {alert['message']}")
```

---
For more details, see:
- [API Documentation](api/)
- [Configuration Guide](configuration_guide.md)
- [Troubleshooting Guide](troubleshooting_guide.md)
- [AI Integration Guide](ai_integration_guide.md) 