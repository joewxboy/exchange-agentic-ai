# Service Metrics Collector

The `ServiceMetricsCollector` class extends the base `MetricsCollector` to provide specialized functionality for collecting and analyzing service-specific metrics in the Open Horizon AI Integration Framework.

## Class Overview

```python
from src.ai.service_metrics import ServiceMetricsCollector
from datetime import timedelta

class ServiceMetricsCollector(MetricsCollector):
    def __init__(self, analysis_window: timedelta = timedelta(minutes=15)):
        super().__init__(analysis_window)
```

## Constructor Parameters

- `analysis_window` (timedelta): The time window for metrics analysis (default: 15 minutes)

## Service-Specific Methods

### _determine_status

```python
def _determine_status(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
    """
    Determine service status based on metrics.
    
    Args:
        stats (Dict[str, Dict[str, float]]): Statistical analysis
        trends (Dict[str, str]): Trend analysis
        
    Returns:
        str: Service status:
            - 'running': Service is running normally
            - 'degraded': Service is running but with issues
            - 'failed': Service has failed
            - 'unknown': Status cannot be determined
    """
```

Determines service status based on:
- CPU usage
- Memory usage
- Error rates
- Response times

### _determine_health

```python
def _determine_health(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
    """
    Determine service health based on metrics.
    
    Args:
        stats (Dict[str, Dict[str, float]]): Statistical analysis
        trends (Dict[str, str]): Trend analysis
        
    Returns:
        str: Service health:
            - 'healthy': Service is healthy
            - 'warning': Service shows warning signs
            - 'critical': Service is in critical condition
            - 'unknown': Health cannot be determined
    """
```

Determines service health based on:
- Error rates
- Resource usage trends
- Response time patterns
- Service-specific metrics

### _generate_alerts

```python
def _generate_alerts(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Generate service-specific alerts.
    
    Args:
        stats (Dict[str, Dict[str, float]]): Statistical analysis
        trends (Dict[str, str]): Trend analysis
        
    Returns:
        List[Dict[str, Any]]: List of generated alerts
    """
```

Generates alerts for:
- High error rates
- Slow response times
- Resource exhaustion
- Service degradation

## Service Metrics

The collector tracks the following service metrics:

1. **Resource Usage**
   - CPU usage percentage
   - Memory usage percentage
   - Disk I/O rates
   - Network bandwidth

2. **Performance Metrics**
   - Response time
   - Request rate
   - Error rate
   - Success rate

3. **Service Health**
   - Service status
   - Health score
   - Uptime
   - Last check time

## Usage Example

```python
from src.ai.service_metrics import ServiceMetricsCollector
from datetime import timedelta

# Create service metrics collector
collector = ServiceMetricsCollector(analysis_window=timedelta(minutes=15))

# Add service metrics
collector.add_metrics({
    'cpu_usage': 65.5,
    'memory_usage': 72.3,
    'error_rate': 0.03,
    'response_time': 250.0
})

# Get recent metrics
recent_metrics = collector.get_recent_metrics()

# Analyze metrics
analysis = collector.analyze_metrics(recent_metrics)

# Print analysis results
print(f"Service Status: {analysis['status']}")
print(f"Service Health: {analysis['health']}")
print("Resource Trends:", analysis['trends'])
print("Service Alerts:", analysis['alerts'])
```

## Best Practices

1. **Metrics Collection**
   - Collect metrics at appropriate intervals
   - Include service-specific metadata
   - Validate metric values
   - Handle service-specific edge cases

2. **Status Determination**
   - Use appropriate thresholds
   - Consider service type
   - Account for normal variations
   - Handle missing metrics

3. **Health Assessment**
   - Monitor multiple indicators
   - Consider service dependencies
   - Track historical patterns
   - Set meaningful thresholds

4. **Alert Generation**
   - Set service-specific thresholds
   - Include service context
   - Prioritize critical alerts
   - Avoid alert storms

## Configuration

The ServiceMetricsCollector can be configured through environment variables:

```bash
# Analysis window (in minutes)
SERVICE_METRICS_WINDOW=15

# Resource thresholds
SERVICE_CPU_THRESHOLD=80
SERVICE_MEMORY_THRESHOLD=85
SERVICE_ERROR_RATE_THRESHOLD=0.05
SERVICE_RESPONSE_TIME_THRESHOLD=1000

# Alert configuration
SERVICE_ALERT_INTERVAL=5
MAX_SERVICE_ALERTS=10
```

## Error Handling

Common error scenarios and handling:

1. **Service-Specific Errors**
   - Handle service unavailability
   - Process service-specific error codes
   - Implement service recovery procedures
   - Log service-specific errors

2. **Metric Collection Errors**
   - Handle missing metrics
   - Process invalid values
   - Implement retry mechanisms
   - Report collection failures

3. **Analysis Errors**
   - Handle insufficient data
   - Process analysis failures
   - Provide fallback values
   - Log analysis errors

## Related Classes

- `MetricsCollector`: Parent class providing base functionality
- `ServiceManagementAgent`: Uses this collector for service management
- `ExchangeAPIClient`: Used for service API communication 