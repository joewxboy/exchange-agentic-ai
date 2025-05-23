# Node Metrics Collector

The `NodeMetricsCollector` class extends the base `MetricsCollector` to provide specialized functionality for collecting and analyzing node-specific metrics in the Open Horizon AI Integration Framework.

## Class Overview

```python
from src.ai.node_metrics import NodeMetricsCollector
from datetime import timedelta

class NodeMetricsCollector(MetricsCollector):
    def __init__(self, analysis_window: timedelta = timedelta(hours=1)):
        super().__init__(analysis_window)
```

## Constructor Parameters

- `analysis_window` (timedelta): The time window for metrics analysis (default: 1 hour)

## Node-Specific Methods

### _determine_status

```python
def _determine_status(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
    """
    Determine node status based on metrics.
    
    Args:
        stats (Dict[str, Dict[str, float]]): Statistical analysis
        trends (Dict[str, str]): Trend analysis
        
    Returns:
        str: Node status:
            - 'online': Node is online and functioning
            - 'degraded': Node is online but with issues
            - 'offline': Node is offline
            - 'unknown': Status cannot be determined
    """
```

Determines node status based on:
- CPU usage
- Memory usage
- Disk usage
- Network connectivity
- Temperature

### _determine_health

```python
def _determine_health(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
    """
    Determine node health based on metrics.
    
    Args:
        stats (Dict[str, Dict[str, float]]): Statistical analysis
        trends (Dict[str, str]): Trend analysis
        
    Returns:
        str: Node health:
            - 'healthy': Node is healthy
            - 'warning': Node shows warning signs
            - 'critical': Node is in critical condition
            - 'unknown': Health cannot be determined
    """
```

Determines node health based on:
- Resource usage trends
- Temperature patterns
- Disk space trends
- Network performance
- Node-specific metrics

### _generate_alerts

```python
def _generate_alerts(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Generate node-specific alerts.
    
    Args:
        stats (Dict[str, Dict[str, float]]): Statistical analysis
        trends (Dict[str, str]): Trend analysis
        
    Returns:
        List[Dict[str, Any]]: List of generated alerts
    """
```

Generates alerts for:
- High CPU usage
- High memory usage
- Low disk space
- High temperature
- Network issues

## Node Metrics

The collector tracks the following node metrics:

1. **Resource Usage**
   - CPU usage percentage
   - Memory usage percentage
   - Disk usage percentage
   - Network bandwidth

2. **Physical Metrics**
   - Temperature
   - Power consumption
   - Fan speed
   - Hardware status

3. **Node Health**
   - Node status
   - Health score
   - Uptime
   - Last check time

## Usage Example

```python
from src.ai.node_metrics import NodeMetricsCollector
from datetime import timedelta

# Create node metrics collector
collector = NodeMetricsCollector(analysis_window=timedelta(hours=1))

# Add node metrics
collector.add_metrics({
    'cpu_usage': 45.5,
    'memory_usage': 62.3,
    'disk_usage': 75.8,
    'temperature': 65.0
})

# Get recent metrics
recent_metrics = collector.get_recent_metrics()

# Analyze metrics
analysis = collector.analyze_metrics(recent_metrics)

# Print analysis results
print(f"Node Status: {analysis['status']}")
print(f"Node Health: {analysis['health']}")
print("Resource Trends:", analysis['trends'])
print("Node Alerts:", analysis['alerts'])
```

## Best Practices

1. **Metrics Collection**
   - Collect metrics at appropriate intervals
   - Include node-specific metadata
   - Validate metric values
   - Handle node-specific edge cases

2. **Status Determination**
   - Use appropriate thresholds
   - Consider node type
   - Account for normal variations
   - Handle missing metrics

3. **Health Assessment**
   - Monitor multiple indicators
   - Consider physical conditions
   - Track historical patterns
   - Set meaningful thresholds

4. **Alert Generation**
   - Set node-specific thresholds
   - Include node context
   - Prioritize critical alerts
   - Avoid alert storms

## Configuration

The NodeMetricsCollector can be configured through environment variables:

```bash
# Analysis window (in minutes)
NODE_METRICS_WINDOW=60

# Resource thresholds
NODE_CPU_THRESHOLD=80
NODE_MEMORY_THRESHOLD=85
NODE_DISK_THRESHOLD=90
NODE_TEMPERATURE_THRESHOLD=75

# Alert configuration
NODE_ALERT_INTERVAL=5
MAX_NODE_ALERTS=10
```

## Error Handling

Common error scenarios and handling:

1. **Node-Specific Errors**
   - Handle node unavailability
   - Process node-specific error codes
   - Implement node recovery procedures
   - Log node-specific errors

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
- `NodeManagementAgent`: Uses this collector for node management
- `ExchangeAPIClient`: Used for node API communication 