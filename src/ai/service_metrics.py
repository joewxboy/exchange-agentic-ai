"""
Service-specific metrics collection and analysis implementation.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from .metrics import MetricsCollector

class ServiceMetricsCollector(MetricsCollector):
    """Collector for service-specific metrics and performance data."""
    
    def __init__(self, client):
        """Initialize the service metrics collector.
        
        Args:
            client: An instance of ExchangeAPIClient
        """
        super().__init__(client)
        self._analysis_window = timedelta(minutes=15)
    
    def collect_service_metrics(self, service_id: str) -> Dict[str, Any]:
        """Collect metrics specific to a service.
        
        Args:
            service_id: ID of the service to collect metrics for
            
        Returns:
            Dictionary containing service metrics
        """
        metrics = self.collect_metrics(service_id)
        
        # Add service-specific analysis
        metrics.update({
            'timestamp': datetime.utcnow().isoformat(),
            'service_id': service_id
        })
        
        return metrics
    
    def analyze_service_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze service health based on collected metrics.
        
        Args:
            metrics: Dictionary containing service metrics
            
        Returns:
            Dictionary containing health analysis
        """
        base_analysis = self.analyze_metrics(metrics)
        
        # Add service-specific health indicators
        service_health = {
            'overall_health': base_analysis['status'],
            'resource_health': {
                'cpu': base_analysis['cpu_status'],
                'memory': base_analysis['memory_status']
            },
            'performance': base_analysis['performance_status'],
            'last_updated': datetime.utcnow().isoformat()
        }
        
        return service_health
    
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