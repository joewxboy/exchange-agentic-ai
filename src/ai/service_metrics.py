from typing import Dict, Any, List
from datetime import timedelta
from .metrics import MetricsCollector

class ServiceMetricsCollector(MetricsCollector):
    """Metrics collector for Open Horizon services."""
    
    def __init__(self):
        """Initialize the service metrics collector."""
        super().__init__()
        self._analysis_window = timedelta(minutes=15)  # Shorter window for services
    
    def _determine_status(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
        """Determine service status based on metrics.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            Status string: 'running', 'degraded', 'failed', or 'unknown'
        """
        if not stats:
            return 'unknown'
        
        # Check for critical metrics
        if 'cpu_usage' in stats and 'memory_usage' in stats:
            cpu_mean = stats['cpu_usage']['mean']
            memory_mean = stats['memory_usage']['mean']
            
            if cpu_mean > 90 or memory_mean > 90:
                return 'failed'
            elif cpu_mean > 70 or memory_mean > 70:
                return 'degraded'
        
        return 'running'
    
    def _determine_health(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
        """Determine service health based on metrics.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            Health string: 'healthy', 'warning', 'critical', or 'unknown'
        """
        if not stats:
            return 'unknown'
        
        # Check for critical metrics
        if 'error_rate' in stats:
            error_rate = stats['error_rate']['mean']
            if error_rate > 0.1:  # 10% error rate
                return 'critical'
            elif error_rate > 0.05:  # 5% error rate
                return 'warning'
        
        # Check for resource usage trends
        if 'cpu_usage' in trends and 'memory_usage' in trends:
            if trends['cpu_usage'] == 'increasing' or trends['memory_usage'] == 'increasing':
                return 'warning'
        
        return 'healthy'
    
    def _generate_alerts(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate service-specific alerts.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            List of alert dictionaries
        """
        alerts = super()._generate_alerts(stats, trends)
        
        # Add service-specific alerts
        if 'error_rate' in stats:
            error_rate = stats['error_rate']['mean']
            if error_rate > 0.1:
                alerts.append({
                    'metric': 'error_rate',
                    'type': 'critical',
                    'message': f'High error rate detected: {error_rate:.1%}'
                })
        
        if 'response_time' in stats:
            response_time = stats['response_time']['mean']
            if response_time > 1000:  # 1 second
                alerts.append({
                    'metric': 'response_time',
                    'type': 'warning',
                    'message': f'High response time detected: {response_time:.0f}ms'
                })
        
        return alerts 