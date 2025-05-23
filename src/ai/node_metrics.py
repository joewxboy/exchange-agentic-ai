from typing import Dict, Any, List
from datetime import timedelta
from .metrics import MetricsCollector

class NodeMetricsCollector(MetricsCollector):
    """Metrics collector for Open Horizon nodes."""
    
    def __init__(self):
        """Initialize the node metrics collector."""
        super().__init__()
        self._analysis_window = timedelta(hours=1)  # Longer window for nodes
    
    def _determine_status(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
        """Determine node status based on metrics.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            Status string: 'online', 'degraded', 'offline', or 'unknown'
        """
        if not stats:
            return 'unknown'
        
        # Check for critical metrics
        if 'cpu_usage' in stats and 'memory_usage' in stats:
            cpu_mean = stats['cpu_usage']['mean']
            memory_mean = stats['memory_usage']['mean']
            
            if cpu_mean > 95 or memory_usage > 95:
                return 'offline'
            elif cpu_mean > 80 or memory_mean > 80:
                return 'degraded'
        
        # Check for disk space
        if 'disk_usage' in stats:
            disk_usage = stats['disk_usage']['mean']
            if disk_usage > 95:
                return 'offline'
            elif disk_usage > 80:
                return 'degraded'
        
        return 'online'
    
    def _determine_health(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> str:
        """Determine node health based on metrics.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            Health string: 'healthy', 'warning', 'critical', or 'unknown'
        """
        if not stats:
            return 'unknown'
        
        # Check for resource usage
        if 'cpu_usage' in stats and 'memory_usage' in stats:
            cpu_mean = stats['cpu_usage']['mean']
            memory_mean = stats['memory_usage']['mean']
            
            if cpu_mean > 90 or memory_mean > 90:
                return 'critical'
            elif cpu_mean > 70 or memory_mean > 70:
                return 'warning'
        
        # Check for temperature if available
        if 'temperature' in stats:
            temp = stats['temperature']['mean']
            if temp > 80:  # 80°C
                return 'critical'
            elif temp > 70:  # 70°C
                return 'warning'
        
        return 'healthy'
    
    def _generate_alerts(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate node-specific alerts.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            List of alert dictionaries
        """
        alerts = super()._generate_alerts(stats, trends)
        
        # Add node-specific alerts
        if 'cpu_usage' in stats:
            cpu_usage = stats['cpu_usage']['mean']
            if cpu_usage > 90:
                alerts.append({
                    'metric': 'cpu_usage',
                    'type': 'critical',
                    'message': f'High CPU usage detected: {cpu_usage:.1f}%'
                })
        
        if 'memory_usage' in stats:
            memory_usage = stats['memory_usage']['mean']
            if memory_usage > 90:
                alerts.append({
                    'metric': 'memory_usage',
                    'type': 'critical',
                    'message': f'High memory usage detected: {memory_usage:.1f}%'
                })
        
        if 'disk_usage' in stats:
            disk_usage = stats['disk_usage']['mean']
            if disk_usage > 90:
                alerts.append({
                    'metric': 'disk_usage',
                    'type': 'critical',
                    'message': f'Low disk space detected: {100 - disk_usage:.1f}% free'
                })
        
        if 'temperature' in stats:
            temp = stats['temperature']['mean']
            if temp > 80:
                alerts.append({
                    'metric': 'temperature',
                    'type': 'critical',
                    'message': f'High temperature detected: {temp:.1f}°C'
                })
        
        return alerts 