# Troubleshooting Guide: Open Horizon AI Integration Framework

This guide helps you identify and resolve common issues when using the Open Horizon AI Integration Framework.

## 1. Common Issues and Solutions

### 1.1. API Connection Issues

#### Symptoms
- Connection timeouts
- Authentication failures
- 401/403 errors
- SSL/TLS errors

#### Solutions
1. **Verify API Credentials**
   ```python
   # Check environment variables
   import os
   print(f"EXCHANGE_URL: {os.getenv('EXCHANGE_URL')}")
   print(f"EXCHANGE_ORG: {os.getenv('EXCHANGE_ORG')}")
   print(f"EXCHANGE_USERNAME: {os.getenv('EXCHANGE_USERNAME')}")
   # Don't print password in logs
   ```

2. **Test API Connection**
   ```python
   from src.exchange.client import ExchangeAPIClient
   client = ExchangeAPIClient(
       base_url="http://localhost:8080",
       org="testorg",
       username="user",
       password="pass"
   )
   try:
       services = client.list_services("testorg")
       print("API connection successful")
   except Exception as e:
       print(f"API connection failed: {str(e)}")
   ```

3. **Check Network Configuration**
   - Verify firewall rules
   - Check proxy settings
   - Ensure DNS resolution works

### 1.2. Metrics Collection Issues

#### Symptoms
- Missing metrics
- Inconsistent data
- High memory usage
- Slow collection

#### Solutions
1. **Verify Metrics Configuration**
   ```python
   from src.ai.metrics import MetricsCollector
   collector = MetricsCollector()
   print(f"Analysis window: {collector._analysis_window}")
   print(f"Max history: {collector._max_history}")
   ```

2. **Check Metrics Cleanup**
   ```python
   # Force cleanup of old metrics
   collector._cleanup_old_metrics()
   print(f"Metrics count: {len(collector.get_recent_metrics())}")
   ```

3. **Monitor Memory Usage**
   ```python
   import psutil
   process = psutil.Process()
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024} MB")
   ```

### 1.3. Alert Generation Issues

#### Symptoms
- Missing alerts
- False positives
- Too many alerts
- Incorrect severity levels

#### Solutions
1. **Verify Alert Thresholds**
   ```python
   import os
   print(f"CPU threshold: {os.getenv('SERVICE_CPU_THRESHOLD')}")
   print(f"Memory threshold: {os.getenv('SERVICE_MEMORY_THRESHOLD')}")
   ```

2. **Test Alert Generation**
   ```python
   from src.ai.service_metrics import ServiceMetricsCollector
   collector = ServiceMetricsCollector()
   collector.add_metrics({'cpu_usage': 90.0, 'memory_usage': 95.0})
   analysis = collector.analyze_metrics(collector.get_recent_metrics())
   print(f"Alerts: {analysis.get('alerts', [])}")
   ```

### 1.4. Agent Action Issues

#### Symptoms
- Failed service updates
- Failed node updates
- Incorrect scaling decisions
- Action timeouts

#### Solutions
1. **Verify Agent Configuration**
   ```python
   from src.ai.service_agent import ServiceManagementAgent
   agent = ServiceManagementAgent(client)
   print(f"Agent state: {agent.state}")
   print(f"Action history: {agent.action_history}")
   ```

2. **Test Agent Actions**
   ```python
   try:
       result = agent.act({
           'action': 'update',
           'service_id': 'test-service',
           'update_data': {'version': '1.0.0'}
       })
       print(f"Action result: {result}")
   except Exception as e:
       print(f"Action failed: {str(e)}")
   ```

## 2. Debugging Tips

### 2.1. Enable Debug Logging
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2.2. Monitor API Calls
```python
import logging
from src.exchange.client import ExchangeAPIClient

class DebugClient(ExchangeAPIClient):
    def _make_request(self, method, path, **kwargs):
        logging.debug(f"API call: {method} {path}")
        response = super()._make_request(method, path, **kwargs)
        logging.debug(f"API response: {response.status_code}")
        return response
```

### 2.3. Profile Performance
```python
import cProfile
import pstats

def profile_function(func):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
    return result
```

## 3. Recovery Procedures

### 3.1. Service Recovery
1. **Check Service Status**
   ```python
   services = client.list_services("testorg")
   for service in services:
       print(f"Service {service['id']}: {service['status']}")
   ```

2. **Restart Failed Service**
   ```python
   service_agent.act({
       'action': 'restart',
       'service_id': 'failed-service'
   })
   ```

### 3.2. Node Recovery
1. **Check Node Health**
   ```python
   nodes = client.list_nodes("testorg")
   for node in nodes:
       print(f"Node {node['id']}: {node['status']}")
   ```

2. **Recover Failed Node**
   ```python
   node_agent.act({
       'action': 'recover',
       'node_id': 'failed-node'
   })
   ```

### 3.3. Metrics Recovery
1. **Reset Metrics Collector**
   ```python
   collector = MetricsCollector()
   collector._metrics = []  # Clear metrics
   collector._cleanup_old_metrics()  # Force cleanup
   ```

2. **Verify Data Collection**
   ```python
   collector.add_metrics({'cpu_usage': 50.0})
   metrics = collector.get_recent_metrics()
   print(f"Metrics count: {len(metrics)}")
   ```

## 4. Best Practices

### 4.1. Error Handling
- Always use try-except blocks for API calls
- Log errors with context
- Implement retry logic for transient failures
- Validate input data before actions

### 4.2. Performance Optimization
- Monitor memory usage
- Clean up old metrics regularly
- Use appropriate analysis windows
- Implement caching where appropriate

### 4.3. Security
- Never log sensitive data
- Rotate credentials regularly
- Use secure connections
- Implement rate limiting

## 5. Getting Help

If you encounter issues not covered in this guide:

1. Check the API documentation in `docs/api/`
2. Review usage examples in `docs/usage_examples.md`
3. Consult the configuration guide in `docs/configuration_guide.md`
4. Open an issue on the project repository
5. Contact the development team

---
For more details, see the API documentation in `docs/api/` and usage examples in `docs/usage_examples.md`. 