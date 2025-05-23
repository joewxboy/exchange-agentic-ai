# Metrics Collector

The `MetricsCollector` class provides the foundation for collecting, analyzing, and managing metrics in the Open Horizon AI Integration Framework. It handles metrics storage, analysis, and alert generation.

## Class Overview

```python
from src.ai.metrics import MetricsCollector
from datetime import timedelta

class MetricsCollector:
    def __init__(self, analysis_window: timedelta = timedelta(hours=1)):
        self._metrics_history = []
        self._analysis_window = analysis_window
```

## Constructor Parameters

- `analysis_window` (timedelta): The time window for metrics analysis (default: 1 hour)

## Core Methods

### add_metrics

```python
def add_metrics(self, metrics: Dict[str, Any]) -> None:
    """
    Add new metrics to the collector.
    
    Args:
        metrics (Dict[str, Any]): Dictionary containing metric values
    """
```

Adds new metrics to the history with a timestamp. Automatically cleans up old metrics.

### get_recent_metrics

```python
def get_recent_metrics(self, window: Optional[timedelta] = None) -> List[Dict[str, Any]]:
    """
    Get metrics from a specific time window.
    
    Args:
        window (Optional[timedelta]): Time window to retrieve metrics from
        
    Returns:
        List[Dict[str, Any]]: List of metrics within the specified window
    """
```

Retrieves metrics from a specified time window. If no window is provided, uses the default analysis window.

### analyze_metrics

```python
def analyze_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze a list of metrics.
    
    Args:
        metrics (List[Dict[str, Any]]): List of metrics to analyze
        
    Returns:
        Dict[str, Any]: Analysis results containing:
            - status: Overall status
            - health: Health assessment
            - trends: Trend analysis
            - alerts: Generated alerts
            - statistics: Statistical analysis
    """
```

Analyzes metrics to determine:
- Overall status
- Health assessment
- Trends
- Alerts
- Statistical analysis

## Analysis Methods

### _extract_numeric_values

```python
def _extract_numeric_values(self, metrics: List[Dict[str, Any]]) -> Dict[str, List[float]]:
    """
    Extract numeric values from metrics.
    
    Args:
        metrics (List[Dict[str, Any]]): List of metrics
        
    Returns:
        Dict[str, List[float]]: Dictionary of metric names to lists of values
    """
```

Extracts numeric values from metrics for statistical analysis.

### _calculate_statistics

```python
def _calculate_statistics(self, numeric_values: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
    """
    Calculate statistics for numeric values.
    
    Args:
        numeric_values (Dict[str, List[float]]): Dictionary of metric names to lists of values
        
    Returns:
        Dict[str, Dict[str, float]]: Statistics for each metric including:
            - mean: Average value
            - median: Median value
            - std_dev: Standard deviation
            - min: Minimum value
            - max: Maximum value
    """
```

Calculates statistical measures for numeric metrics.

### _analyze_trends

```python
def _analyze_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Analyze trends in metrics.
    
    Args:
        metrics (List[Dict[str, Any]]): List of metrics
        
    Returns:
        Dict[str, str]: Dictionary of metric names to trend descriptions:
            - 'increasing': Values are increasing
            - 'decreasing': Values are decreasing
            - 'stable': Values are stable
    """
```

Analyzes trends in metrics over time.

### _generate_alerts

```python
def _generate_alerts(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> List[Dict[str, Any]]:
    """
    Generate alerts based on statistics and trends.
    
    Args:
        stats (Dict[str, Dict[str, float]]): Statistical analysis
        trends (Dict[str, str]): Trend analysis
        
    Returns:
        List[Dict[str, Any]]: List of generated alerts
    """
```

Generates alerts based on:
- Statistical anomalies
- Trend changes
- Threshold violations
- Pattern detection

## Usage Example

```python
from src.ai.metrics import MetricsCollector
from datetime import timedelta

# Create metrics collector
collector = MetricsCollector(analysis_window=timedelta(minutes=30))

# Add metrics
collector.add_metrics({
    'cpu_usage': 75.5,
    'memory_usage': 82.3,
    'error_rate': 0.02
})

# Get recent metrics
recent_metrics = collector.get_recent_metrics(timedelta(minutes=15))

# Analyze metrics
analysis = collector.analyze_metrics(recent_metrics)

# Print analysis results
print(f"Status: {analysis['status']}")
print(f"Health: {analysis['health']}")
print("Trends:", analysis['trends'])
print("Alerts:", analysis['alerts'])
print("Statistics:", analysis['statistics'])
```

## Best Practices

1. **Metrics Collection**
   - Collect metrics at appropriate intervals
   - Include timestamps with metrics
   - Validate metric values
   - Handle missing or invalid data

2. **Analysis**
   - Use appropriate time windows
   - Consider metric relationships
   - Account for seasonality
   - Handle outliers appropriately

3. **Alert Generation**
   - Set meaningful thresholds
   - Avoid alert storms
   - Include context in alerts
   - Prioritize alerts appropriately

4. **Performance**
   - Clean up old metrics
   - Optimize storage
   - Cache analysis results
   - Monitor collector performance

## Related Classes

- `ServiceMetricsCollector`: Specialized collector for service metrics
- `NodeMetricsCollector`: Specialized collector for node metrics

## Configuration

The MetricsCollector can be configured through environment variables:

```bash
# Analysis window (in minutes)
METRICS_ANALYSIS_WINDOW=60

# Cleanup interval (in minutes)
METRICS_CLEANUP_INTERVAL=30

# Maximum history size
MAX_METRICS_HISTORY=1000
```

## Error Handling

Common error scenarios and handling:

1. **Invalid Metrics**
   - Log invalid metrics
   - Skip invalid entries
   - Report validation errors

2. **Storage Issues**
   - Implement cleanup procedures
   - Handle storage limits
   - Backup critical metrics

3. **Analysis Errors**
   - Handle missing data
   - Report analysis failures
   - Provide fallback values 