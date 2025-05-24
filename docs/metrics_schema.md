# Metrics Data Schema

This document provides a comprehensive overview of the metrics data structures used in the Open Horizon AI Integration Framework.

## Base Metrics Structure

All metrics include a timestamp and basic resource usage metrics:

```python
{
    'timestamp': datetime,  # When the metrics were collected
    'cpu_usage': float,     # CPU usage percentage (0-100)
    'memory_usage': float,  # Memory usage percentage (0-100)
    'error_rate': float     # Error rate (0.0 to 1.0)
}
```

## Service Metrics Structure

Service metrics extend the base metrics with service-specific measurements:

```python
{
    'timestamp': datetime,
    'cpu_usage': float,
    'memory_usage': float,
    'memory_rss': float,    # Memory usage in MB
    'response_time': float, # Response time in milliseconds
    'error_rate': float,
    'threads': int,        # Number of threads
    'open_files': int,     # Number of open files
    'connections': int     # Number of active connections
}
```

## Node Metrics Structure

Node metrics extend the base metrics with node-specific measurements:

```python
{
    'timestamp': datetime,
    'cpu_usage': float,
    'memory_usage': float,
    'disk_usage': float,   # Disk usage percentage
    'temperature': float   # Node temperature
}
```

## Analysis Results Structure

The analysis results provide insights into the metrics:

```python
{
    'status': str,         # 'healthy', 'degraded', 'failed', 'unknown'
    'health': str,         # 'healthy', 'warning', 'critical', 'unknown'
    'alerts': List[Dict],  # List of alerts
    'recommendations': List[Dict],  # List of recommendations
    'metrics': {
        'cpu_usage': float,
        'memory_usage': float,
        'response_time': float,
        'error_rate': float
    }
}
```

## Alert Structure

Alerts generated from metrics analysis:

```python
{
    'type': str,           # Alert type (e.g., 'high_cpu', 'high_memory')
    'severity': str,       # 'info', 'warning', 'critical'
    'message': str,        # Human-readable alert message
    'timestamp': datetime, # When the alert was generated
    'metric': str,         # Which metric triggered the alert
    'value': float,        # The value that triggered the alert
    'threshold': float     # The threshold that was exceeded
}
```

## Thresholds

Default thresholds for metrics analysis:

```python
# Service Metrics Thresholds
SERVICE_CPU_THRESHOLD = 80.0        # CPU usage percentage
SERVICE_MEMORY_THRESHOLD = 85.0     # Memory usage percentage
SERVICE_ERROR_RATE_THRESHOLD = 0.05 # Error rate (5%)
SERVICE_RESPONSE_TIME_THRESHOLD = 1000.0  # Response time in ms

# Node Metrics Thresholds
NODE_CPU_THRESHOLD = 80.0           # CPU usage percentage
NODE_MEMORY_THRESHOLD = 85.0        # Memory usage percentage
NODE_DISK_THRESHOLD = 90.0          # Disk usage percentage
NODE_TEMPERATURE_THRESHOLD = 75.0   # Temperature in Celsius
```

## Metric Collection

Metrics are collected and stored with the following characteristics:

1. **Collection Frequency**:
   - Service metrics: Every 15 minutes by default
   - Node metrics: Every 60 minutes by default

2. **History Retention**:
   - Default: 1000 data points per service/node
   - Configurable via environment variables

3. **Data Cleanup**:
   - Automatic cleanup of old metrics
   - Configurable retention period

## Analysis Methods

The metrics are analyzed using several methods:

1. **Statistical Analysis**:
   - Mean, median, min, max values
   - Standard deviation
   - Percentiles

2. **Trend Detection**:
   - Increasing trends
   - Decreasing trends
   - Stable patterns

3. **Anomaly Detection**:
   - Statistical outliers
   - Pattern deviations
   - Threshold violations

## Configuration

Metrics collection and analysis can be configured through environment variables:

```bash
# Analysis windows
SERVICE_METRICS_WINDOW=15    # Minutes
NODE_METRICS_WINDOW=60       # Minutes

# History retention
MAX_METRICS_HISTORY=1000     # Data points

# Cleanup intervals
METRICS_CLEANUP_INTERVAL=30  # Minutes

# Alert configuration
ALERT_INTERVAL=5            # Minutes
MAX_ALERTS=10              # Per service/node
```

## Best Practices

1. **Metrics Collection**:
   - Collect metrics at appropriate intervals
   - Include timestamps with all metrics
   - Validate metric values
   - Handle missing or invalid data

2. **Analysis**:
   - Use appropriate time windows
   - Consider metric relationships
   - Account for seasonality
   - Handle outliers appropriately

3. **Alert Generation**:
   - Set meaningful thresholds
   - Avoid alert storms
   - Include context in alerts
   - Prioritize alerts appropriately

4. **Performance**:
   - Clean up old metrics
   - Optimize storage
   - Cache analysis results
   - Monitor collector performance 