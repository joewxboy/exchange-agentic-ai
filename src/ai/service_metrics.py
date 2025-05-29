"""
Service metrics collector that derives metrics from available service data.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psutil
import requests
import time
import logging
from .metrics import BaseMetricsCollector

class ServiceMetricsCollector(BaseMetricsCollector):
    """Collects and analyzes service metrics by deriving them from available data."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the service metrics collector.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._response_times: Dict[str, List[float]] = {}
        self._error_counts: Dict[str, int] = {}
        self._request_counts: Dict[str, int] = {}
        
        # Set default thresholds from config or use defaults
        self.thresholds = {
            'cpu_warning': self.config.get('cpu_warning_threshold', 80),
            'cpu_critical': self.config.get('cpu_critical_threshold', 90),
            'memory_warning': self.config.get('memory_warning_threshold', 80),
            'memory_critical': self.config.get('memory_critical_threshold', 90),
            'response_warning': self.config.get('response_warning_threshold', 1000),
            'response_critical': self.config.get('response_critical_threshold', 2000),
            'error_warning': self.config.get('error_warning_threshold', 0.05),
            'error_critical': self.config.get('error_critical_threshold', 0.10)
        }
    
    def _collect_entity_metrics(self, service_id: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics for a service.
        
        Args:
            service_id: ID of the service
            service_data: Service data from the API
            
        Returns:
            Dictionary containing collected metrics
        """
        try:
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
                'cpu_usage': container_metrics.get('cpu_usage', 0.0),
                'memory_usage': container_metrics.get('memory_usage', 0.0),
                'memory_rss': container_metrics.get('memory_rss', 0.0),
                'response_time': response_time,
                'error_rate': error_rate,
                'threads': container_metrics.get('threads', 0),
                'open_files': container_metrics.get('open_files', 0),
                'connections': container_metrics.get('connections', 0)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Failed to collect metrics for service {service_id}: {str(e)}")
            return {}
    
    def _get_container_metrics(self, service_id: str) -> Dict[str, float]:
        """Get container metrics using psutil.
        
        Args:
            service_id: ID of the service
            
        Returns:
            Dictionary containing container metrics
        """
        try:
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
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            self.logger.warning(f"Failed to get container metrics for {service_id}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error getting container metrics for {service_id}: {str(e)}")
        return {}
    
    def _measure_response_time(self, service_id: str, url: str) -> float:
        """Measure service response time.
        
        Args:
            service_id: ID of the service
            url: URL to measure response time for
            
        Returns:
            Response time in milliseconds
        """
        try:
            start_time = time.time()
            response = requests.get(url, timeout=5)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            response.raise_for_status()
            
            # Update response time history
            if service_id not in self._response_times:
                self._response_times[service_id] = []
            self._response_times[service_id].append(response_time)
            
            # Update request counts
            self._request_counts[service_id] = self._request_counts.get(service_id, 0) + 1
            
            return response_time
            
        except requests.RequestException as e:
            self.logger.warning(f"Failed to measure response time for {service_id}: {str(e)}")
            # Update error counts
            self._error_counts[service_id] = self._error_counts.get(service_id, 0) + 1
            return float('inf')
        except Exception as e:
            self.logger.error(f"Unexpected error measuring response time for {service_id}: {str(e)}")
            return float('inf')
    
    def _calculate_error_rate(self, service_id: str) -> float:
        """Calculate error rate from recent requests.
        
        Args:
            service_id: ID of the service
            
        Returns:
            Error rate as a float between 0 and 1
        """
        request_count = self._request_counts.get(service_id, 0)
        error_count = self._error_counts.get(service_id, 0)
        
        if request_count == 0:
            return 0.0
        
        return error_count / request_count
    
    def _analyze_entity_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze metrics for a service.
        
        Args:
            metrics: Dictionary containing metric values
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            status = 'healthy'
            health = 'good'
            alerts = []
            recommendations = []
            
            # Check CPU usage
            cpu_usage = metrics.get('cpu_usage', 0.0)
            if cpu_usage > self.thresholds['cpu_critical']:
                status = 'critical'
                health = 'poor'
                alerts.append('Critical CPU usage')
                recommendations.append('Immediate CPU scaling required')
            elif cpu_usage > self.thresholds['cpu_warning']:
                status = 'warning'
                alerts.append('High CPU usage')
                recommendations.append('Consider scaling up CPU resources')
            
            # Check memory usage
            memory_usage = metrics.get('memory_usage', 0.0)
            if memory_usage > self.thresholds['memory_critical']:
                status = 'critical'
                health = 'poor'
                alerts.append('Critical memory usage')
                recommendations.append('Immediate memory scaling required')
            elif memory_usage > self.thresholds['memory_warning']:
                status = 'warning'
                alerts.append('High memory usage')
                recommendations.append('Consider scaling up memory resources')
            
            # Check response time
            response_time = metrics.get('response_time', float('inf'))
            if response_time > self.thresholds['response_critical']:
                status = 'critical'
                health = 'poor'
                alerts.append('Critical response time')
                recommendations.append('Immediate performance optimization required')
            elif response_time > self.thresholds['response_warning']:
                status = 'warning'
                alerts.append('High response time')
                recommendations.append('Investigate performance bottlenecks')
            
            # Check error rate
            error_rate = metrics.get('error_rate', 0.0)
            if error_rate > self.thresholds['error_critical']:
                status = 'critical'
                health = 'poor'
                alerts.append('Critical error rate')
                recommendations.append('Immediate error investigation required')
            elif error_rate > self.thresholds['error_warning']:
                status = 'warning'
                alerts.append('High error rate')
                recommendations.append('Investigate error sources')
            
            return {
                'status': status,
                'health': health,
                'alerts': alerts,
                'recommendations': recommendations,
                'metrics': metrics
            }
            
        except Exception as e:
            self.logger.error(f"Failed to analyze metrics: {str(e)}")
            return {
                'status': 'unknown',
                'health': 'unknown',
                'alerts': [{'type': 'error', 'message': str(e)}],
                'recommendations': []
            } 