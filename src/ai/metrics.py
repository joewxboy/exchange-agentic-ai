from typing import Dict, Any, List
from datetime import datetime, timedelta
import statistics

class MetricsCollector:
    """Base class for collecting and analyzing metrics."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self._metrics_history: List[Dict[str, Any]] = []
        self._analysis_window = timedelta(hours=1)  # Default analysis window
    
    def add_metrics(self, metrics: Dict[str, Any]) -> None:
        """Add new metrics to the history.
        
        Args:
            metrics: Dictionary containing metrics data
        """
        self._metrics_history.append({
            'timestamp': datetime.utcnow().isoformat(),
            'data': metrics
        })
        self._cleanup_old_metrics()
    
    def get_recent_metrics(self, window: timedelta = None) -> List[Dict[str, Any]]:
        """Get metrics from the specified time window.
        
        Args:
            window: Time window to get metrics for (defaults to analysis_window)
            
        Returns:
            List of metrics within the time window
        """
        window = window or self._analysis_window
        cutoff = datetime.utcnow() - window
        
        return [
            m for m in self._metrics_history
            if datetime.fromisoformat(m['timestamp']) > cutoff
        ]
    
    def analyze_metrics(self, metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze a list of metrics.
        
        Args:
            metrics: List of metrics to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if not metrics:
            return {
                'status': 'unknown',
                'health': 'unknown',
                'trends': {},
                'alerts': []
            }
        
        # Extract numeric values for analysis
        numeric_values = self._extract_numeric_values(metrics)
        
        # Calculate basic statistics
        stats = self._calculate_statistics(numeric_values)
        
        # Determine trends
        trends = self._analyze_trends(metrics)
        
        # Generate alerts
        alerts = self._generate_alerts(stats, trends)
        
        return {
            'status': self._determine_status(stats, trends),
            'health': self._determine_health(stats, trends),
            'trends': trends,
            'alerts': alerts,
            'statistics': stats
        }
    
    def _cleanup_old_metrics(self) -> None:
        """Remove metrics older than the analysis window."""
        cutoff = datetime.utcnow() - self._analysis_window
        self._metrics_history = [
            m for m in self._metrics_history
            if datetime.fromisoformat(m['timestamp']) > cutoff
        ]
    
    def _extract_numeric_values(self, metrics: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Extract numeric values from metrics for analysis.
        
        Args:
            metrics: List of metrics to extract values from
            
        Returns:
            Dictionary mapping metric names to lists of values
        """
        numeric_values = {}
        
        for metric in metrics:
            for key, value in metric['data'].items():
                if isinstance(value, (int, float)):
                    if key not in numeric_values:
                        numeric_values[key] = []
                    numeric_values[key].append(value)
        
        return numeric_values
    
    def _calculate_statistics(self, numeric_values: Dict[str, List[float]]) -> Dict[str, Dict[str, float]]:
        """Calculate basic statistics for numeric values.
        
        Args:
            numeric_values: Dictionary mapping metric names to lists of values
            
        Returns:
            Dictionary containing statistics for each metric
        """
        stats = {}
        
        for metric, values in numeric_values.items():
            if len(values) > 0:
                stats[metric] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                }
        
        return stats
    
    def _analyze_trends(self, metrics: List[Dict[str, Any]]) -> Dict[str, str]:
        """Analyze trends in metrics over time.
        
        Args:
            metrics: List of metrics to analyze
            
        Returns:
            Dictionary mapping metric names to trend descriptions
        """
        trends = {}
        numeric_values = self._extract_numeric_values(metrics)
        
        for metric, values in numeric_values.items():
            if len(values) < 2:
                trends[metric] = 'insufficient_data'
                continue
            
            # Calculate simple linear regression
            x = range(len(values))
            slope = statistics.linear_regression(x, values)[0]
            
            if abs(slope) < 0.01:
                trends[metric] = 'stable'
            elif slope > 0:
                trends[metric] = 'increasing'
            else:
                trends[metric] = 'decreasing'
        
        return trends
    
    def _generate_alerts(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate alerts based on statistics and trends.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        for metric, metric_stats in stats.items():
            # Check for high standard deviation
            if metric_stats['std_dev'] > metric_stats['mean'] * 0.5:
                alerts.append({
                    'metric': metric,
                    'type': 'high_variance',
                    'message': f'High variance detected in {metric}'
                })
            
            # Check for extreme values
            if metric_stats['max'] > metric_stats['mean'] * 2:
                alerts.append({
                    'metric': metric,
                    'type': 'extreme_value',
                    'message': f'Extreme high value detected in {metric}'
                })
        
        return alerts
    
    def _determine_status(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
        """Determine overall status based on statistics and trends.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            Status string
        """
        # Implement status determination logic
        return 'normal'  # Placeholder
    
    def _determine_health(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
        """Determine overall health based on statistics and trends.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            Health string
        """
        # Implement health determination logic
        return 'healthy'  # Placeholder 