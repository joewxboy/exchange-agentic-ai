"""
Service metrics collector that derives metrics from available service data.
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import psutil
import requests
import time
from .metrics import BaseMetricsCollector

class ServiceMetricsCollector(BaseMetricsCollector):
    """Collects and analyzes service metrics by deriving them from available data."""
    
    def __init__(self):
        super().__init__()
        self._metrics_history = {}
        self._last_check = {}
        self._response_times = {}
    
    def _get_container_metrics(self, service_id: str) -> Dict[str, float]:
        """Get container metrics using psutil."""
        try:
            # Find the container process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if service_id in str(proc.info['cmdline']):
                    process = psutil.Process(proc.info['pid'])
                    return {
                        'cpu_usage': process.cpu_percent(),
                        'memory_usage': process.memory_percent(),
                        'memory_rss': process.memory_info().rss / 1024 / 1024,  # MB
                        'threads': process.num_threads(),
                        'open_files': len(process.open_files()),
                        'connections': len(process.connections())
                    }
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        return {}
    
    def _measure_response_time(self, service_id: str, url: str) -> float:
        """Measure service response time."""
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            response.raise_for_status()
            return response_time
        except requests.RequestException:
            return float('inf')
    
    def _calculate_error_rate(self, service_id: str) -> float:
        """Calculate error rate from recent requests."""
        if service_id not in self._metrics_history:
            return 0.0
        
        recent_metrics = self._metrics_history[service_id][-10:]  # Last 10 measurements
        if not recent_metrics:
            return 0.0
        
        error_count = sum(1 for m in recent_metrics if m.get('error', False))
        return error_count / len(recent_metrics)
    
    def collect_metrics(self, service_id: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics for a service by deriving them from available data."""
        current_time = datetime.now()
        
        # Initialize metrics history if needed
        if service_id not in self._metrics_history:
            self._metrics_history[service_id] = []
        
        # Get container metrics
        container_metrics = self._get_container_metrics(service_id)
        
        # Measure response time if URL is available
        response_time = float('inf')
        if 'url' in service_data:
            response_time = self._measure_response_time(service_id, service_data['url'])
        
        # Calculate error rate
        error_rate = self._calculate_error_rate(service_id)
        
        # Combine all metrics
        metrics = {
            'timestamp': current_time,
            'cpu_usage': container_metrics.get('cpu_usage', 0.0),
            'memory_usage': container_metrics.get('memory_usage', 0.0),
            'memory_rss': container_metrics.get('memory_rss', 0.0),
            'response_time': response_time,
            'error_rate': error_rate,
            'threads': container_metrics.get('threads', 0),
            'open_files': container_metrics.get('open_files', 0),
            'connections': container_metrics.get('connections', 0)
        }
        
        # Store metrics in history
        self._metrics_history[service_id].append(metrics)
        
        # Clean up old metrics
        self._cleanup_old_metrics(service_id)
        
        return metrics
    
    def _cleanup_old_metrics(self, service_id: str, max_history: int = 1000):
        """Clean up old metrics from history."""
        if service_id in self._metrics_history:
            self._metrics_history[service_id] = self._metrics_history[service_id][-max_history:]
    
    def get_metrics_history(self, service_id: str, window_minutes: int = 60) -> List[Dict[str, Any]]:
        """Get metrics history for a service within the specified time window."""
        if service_id not in self._metrics_history:
            return []
        
        cutoff_time = datetime.now() - timedelta(minutes=window_minutes)
        return [
            m for m in self._metrics_history[service_id]
            if m['timestamp'] >= cutoff_time
        ]
    
    def analyze_metrics(self, service_id: str) -> Dict[str, Any]:
        """Analyze metrics for a service and determine its health status."""
        if service_id not in self._metrics_history:
            return {
                'status': 'unknown',
                'health': 'unknown',
                'alerts': [],
                'recommendations': []
            }
        
        recent_metrics = self.get_metrics_history(service_id)
        if not recent_metrics:
            return {
                'status': 'unknown',
                'health': 'unknown',
                'alerts': [],
                'recommendations': []
            }
        
        # Calculate averages
        avg_cpu = sum(m['cpu_usage'] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m['memory_usage'] for m in recent_metrics) / len(recent_metrics)
        avg_response = sum(m['response_time'] for m in recent_metrics) / len(recent_metrics)
        avg_error_rate = sum(m['error_rate'] for m in recent_metrics) / len(recent_metrics)
        
        # Determine status and health
        status = 'healthy'
        health = 'good'
        alerts = []
        recommendations = []
        
        # Check CPU usage
        if avg_cpu > 80:
            status = 'warning'
            alerts.append('High CPU usage')
            recommendations.append('Consider scaling up CPU resources')
        elif avg_cpu > 90:
            status = 'critical'
            health = 'poor'
            alerts.append('Critical CPU usage')
            recommendations.append('Immediate CPU scaling required')
        
        # Check memory usage
        if avg_memory > 80:
            status = 'warning'
            alerts.append('High memory usage')
            recommendations.append('Consider scaling up memory resources')
        elif avg_memory > 90:
            status = 'critical'
            health = 'poor'
            alerts.append('Critical memory usage')
            recommendations.append('Immediate memory scaling required')
        
        # Check response time
        if avg_response > 1000:
            status = 'warning'
            alerts.append('High response time')
            recommendations.append('Investigate performance bottlenecks')
        elif avg_response > 2000:
            status = 'critical'
            health = 'poor'
            alerts.append('Critical response time')
            recommendations.append('Immediate performance optimization required')
        
        # Check error rate
        if avg_error_rate > 0.05:
            status = 'warning'
            alerts.append('High error rate')
            recommendations.append('Investigate error sources')
        elif avg_error_rate > 0.10:
            status = 'critical'
            health = 'poor'
            alerts.append('Critical error rate')
            recommendations.append('Immediate error investigation required')
        
        return {
            'status': status,
            'health': health,
            'alerts': alerts,
            'recommendations': recommendations,
            'metrics': {
                'cpu_usage': avg_cpu,
                'memory_usage': avg_memory,
                'response_time': avg_response,
                'error_rate': avg_error_rate
            }
        } 