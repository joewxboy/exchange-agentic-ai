"""
Node metrics collector implementation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from .metrics import BaseMetricsCollector

class NodeMetricsCollector(BaseMetricsCollector):
    """Metrics collector for Open Horizon nodes."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the node metrics collector.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._analysis_window = timedelta(hours=1)  # Longer window for nodes
        
        # Set default thresholds from config or use defaults
        self.thresholds = {
            'cpu_warning': self.config.get('cpu_warning_threshold', 70),
            'cpu_critical': self.config.get('cpu_critical_threshold', 90),
            'memory_warning': self.config.get('memory_warning_threshold', 70),
            'memory_critical': self.config.get('memory_critical_threshold', 90),
            'disk_warning': self.config.get('disk_warning_threshold', 80),
            'disk_critical': self.config.get('disk_critical_threshold', 95),
            'temp_warning': self.config.get('temp_warning_threshold', 70),
            'temp_critical': self.config.get('temp_critical_threshold', 80)
        }
    
    def _collect_entity_metrics(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics for a node.
        
        Args:
            node_id: ID of the node
            node_data: Node data from the API
            
        Returns:
            Dictionary containing node metrics
        """
        try:
            metrics = {
                'node_id': node_id,
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'disk_usage': 0.0,
                'temperature': 0.0
            }
            
            # Extract metrics from node data
            if 'status' in node_data:
                status = node_data['status']
                if 'resources' in status:
                    resources = status['resources']
                    metrics['cpu_usage'] = resources.get('cpu', 0.0)
                    metrics['memory_usage'] = resources.get('memory', 0.0)
                    metrics['disk_usage'] = resources.get('disk', 0.0)
                
                if 'temperature' in status:
                    metrics['temperature'] = status['temperature']
            
            # Add any additional metrics from node data
            if 'metrics' in node_data:
                metrics.update(node_data['metrics'])
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics for node {node_id}: {str(e)}")
            return {}
    
    def _analyze_entity_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metrics for a node.
        
        Args:
            metrics: Dictionary containing metric values
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Calculate statistics
            stats = self._calculate_statistics(metrics)
            
            # Determine trends
            trends = self._determine_trends(metrics)
            
            # Determine status and health
            status = self._determine_status(stats, trends)
            health = self._determine_health(stats, trends)
            
            # Generate alerts
            alerts = self._generate_alerts(stats, trends)
            
            return {
                'status': status,
                'health': health,
                'alerts': alerts,
                'metrics': metrics,
                'statistics': stats,
                'trends': trends
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze metrics: {str(e)}")
            return {
                'status': 'unknown',
                'health': 'unknown',
                'alerts': [{'type': 'error', 'message': str(e)}],
                'metrics': metrics
            }
    
    def _calculate_statistics(self, metrics: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """Calculate statistics for metrics.
        
        Args:
            metrics: Dictionary containing metric values
            
        Returns:
            Dictionary containing statistics for each metric
        """
        stats = {}
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                stats[key] = {
                    'mean': value,
                    'min': value,
                    'max': value
                }
        return stats
    
    def _determine_trends(self, metrics: Dict[str, Any]) -> Dict[str, str]:
        """Determine trends in metrics.
        
        Args:
            metrics: Dictionary containing metric values
            
        Returns:
            Dictionary containing trend information
        """
        trends = {}
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                if len(self.metrics_history) > 0:
                    prev_value = self.metrics_history[-1].get(key, value)
                    if value > prev_value * 1.1:
                        trends[key] = 'increasing'
                    elif value < prev_value * 0.9:
                        trends[key] = 'decreasing'
                    else:
                        trends[key] = 'stable'
                else:
                    trends[key] = 'unknown'
        return trends
    
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
            
            if cpu_mean > self.thresholds['cpu_critical'] or memory_mean > self.thresholds['memory_critical']:
                return 'offline'
            elif cpu_mean > self.thresholds['cpu_warning'] or memory_mean > self.thresholds['memory_warning']:
                return 'degraded'
        
        # Check for disk space
        if 'disk_usage' in stats:
            disk_usage = stats['disk_usage']['mean']
            if disk_usage > self.thresholds['disk_critical']:
                return 'offline'
            elif disk_usage > self.thresholds['disk_warning']:
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
            
            if cpu_mean > self.thresholds['cpu_critical'] or memory_mean > self.thresholds['memory_critical']:
                return 'critical'
            elif cpu_mean > self.thresholds['cpu_warning'] or memory_mean > self.thresholds['memory_warning']:
                return 'warning'
        
        # Check for temperature if available
        if 'temperature' in stats:
            temp = stats['temperature']['mean']
            if temp > self.thresholds['temp_critical']:
                return 'critical'
            elif temp > self.thresholds['temp_warning']:
                return 'warning'
        
        return 'healthy'
    
    def _generate_alerts(self, stats: Dict[str, Dict[str, float]], trends: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate alerts based on metrics.
        
        Args:
            stats: Statistics for each metric
            trends: Trends for each metric
            
        Returns:
            List of alert dictionaries
        """
        alerts = []
        
        # Check CPU usage
        if 'cpu_usage' in stats:
            cpu_mean = stats['cpu_usage']['mean']
            if cpu_mean > self.thresholds['cpu_critical']:
                alerts.append({
                    'type': 'critical',
                    'message': f'CPU usage is critical: {cpu_mean:.1f}%'
                })
            if cpu_mean > self.thresholds['cpu_warning']:
                alerts.append({
                    'type': 'warning',
                    'message': f'CPU usage is high: {cpu_mean:.1f}%'
                })
        
        # Check memory usage
        if 'memory_usage' in stats:
            memory_mean = stats['memory_usage']['mean']
            if memory_mean > self.thresholds['memory_critical']:
                alerts.append({
                    'type': 'critical',
                    'message': f'Memory usage is critical: {memory_mean:.1f}%'
                })
            if memory_mean > self.thresholds['memory_warning']:
                alerts.append({
                    'type': 'warning',
                    'message': f'Memory usage is high: {memory_mean:.1f}%'
                })
        
        # Check disk usage
        if 'disk_usage' in stats:
            disk_mean = stats['disk_usage']['mean']
            if disk_mean > self.thresholds['disk_critical']:
                alerts.append({
                    'type': 'critical',
                    'message': f'Disk usage is critical: {disk_mean:.1f}%'
                })
            if disk_mean > self.thresholds['disk_warning']:
                alerts.append({
                    'type': 'warning',
                    'message': f'Disk usage is high: {disk_mean:.1f}%'
                })
        
        # Check temperature
        if 'temperature' in stats:
            temp_mean = stats['temperature']['mean']
            if temp_mean > self.thresholds['temp_critical']:
                alerts.append({
                    'type': 'critical',
                    'message': f'Temperature is critical: {temp_mean:.1f}°C'
                })
            if temp_mean > self.thresholds['temp_warning']:
                alerts.append({
                    'type': 'warning',
                    'message': f'Temperature is high: {temp_mean:.1f}°C'
                })
        
        return alerts 