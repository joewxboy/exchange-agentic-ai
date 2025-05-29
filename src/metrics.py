from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import json
import os

@dataclass
class MetricPoint:
    """Represents a single metric data point."""
    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)

@dataclass
class Metric:
    """Represents a metric with multiple data points."""
    name: str
    description: str
    type: str  # counter, gauge, histogram
    points: List[MetricPoint] = field(default_factory=list)
    labels: Dict[str, str] = field(default_factory=dict)

class MetricsCollector:
    """Base class for collecting metrics."""
    
    def __init__(self, metrics_dir: str = "metrics"):
        self.metrics_dir = metrics_dir
        self._metrics: Dict[str, Metric] = {}
        self._ensure_metrics_dir()
    
    def _ensure_metrics_dir(self):
        """Ensure metrics directory exists."""
        if not os.path.exists(self.metrics_dir):
            os.makedirs(self.metrics_dir)
    
    def add_metric(self, name: str, description: str, metric_type: str, labels: Optional[Dict[str, str]] = None):
        """Add a new metric to track."""
        if name in self._metrics:
            raise ValueError(f"Metric {name} already exists")
        
        self._metrics[name] = Metric(
            name=name,
            description=description,
            type=metric_type,
            labels=labels or {}
        )
    
    def record_point(self, metric_name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a new data point for a metric."""
        if metric_name not in self._metrics:
            raise ValueError(f"Metric {metric_name} does not exist")
        
        metric = self._metrics[metric_name]
        point = MetricPoint(
            timestamp=datetime.now(),
            value=value,
            labels=labels or {}
        )
        metric.points.append(point)
    
    def get_metric(self, name: str) -> Optional[Metric]:
        """Get a metric by name."""
        return self._metrics.get(name)
    
    def get_all_metrics(self) -> Dict[str, Metric]:
        """Get all metrics."""
        return self._metrics.copy()
    
    def save_metrics(self):
        """Save metrics to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.metrics_dir, f"metrics_{timestamp}.json")
        
        metrics_data = {}
        for name, metric in self._metrics.items():
            metrics_data[name] = {
                "description": metric.description,
                "type": metric.type,
                "labels": metric.labels,
                "points": [
                    {
                        "timestamp": point.timestamp.isoformat(),
                        "value": point.value,
                        "labels": point.labels
                    }
                    for point in metric.points
                ]
            }
        
        with open(filename, 'w') as f:
            json.dump(metrics_data, f, indent=2)

class OrganizationMetricsCollector(MetricsCollector):
    """Collector for organization-related metrics."""
    
    def __init__(self, metrics_dir: str = "metrics"):
        super().__init__(metrics_dir)
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Set up organization-specific metrics."""
        # Organization operations
        self.add_metric(
            "organization_operations_total",
            "Total number of organization operations",
            "counter",
            {"operation_type": "all"}
        )
        
        # User operations
        self.add_metric(
            "user_operations_total",
            "Total number of user operations",
            "counter",
            {"operation_type": "all"}
        )
        
        # Cache hits/misses
        self.add_metric(
            "cache_hits_total",
            "Total number of cache hits",
            "counter"
        )
        self.add_metric(
            "cache_misses_total",
            "Total number of cache misses",
            "counter"
        )
        
        # Response times
        self.add_metric(
            "api_response_time_seconds",
            "API response time in seconds",
            "histogram",
            {"operation_type": "all"}
        )
        
        # Error rates
        self.add_metric(
            "error_rate_total",
            "Total number of errors",
            "counter",
            {"error_type": "all"}
        )
    
    def record_organization_operation(self, operation_type: str, success: bool):
        """Record an organization operation."""
        self.record_point(
            "organization_operations_total",
            1.0,
            {"operation_type": operation_type, "success": str(success)}
        )
    
    def record_user_operation(self, operation_type: str, success: bool):
        """Record a user operation."""
        self.record_point(
            "user_operations_total",
            1.0,
            {"operation_type": operation_type, "success": str(success)}
        )
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.record_point("cache_hits_total", 1.0)
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.record_point("cache_misses_total", 1.0)
    
    def record_response_time(self, operation_type: str, seconds: float):
        """Record API response time."""
        self.record_point(
            "api_response_time_seconds",
            seconds,
            {"operation_type": operation_type}
        )
    
    def record_error(self, error_type: str):
        """Record an error."""
        self.record_point(
            "error_rate_total",
            1.0,
            {"error_type": error_type}
        ) 