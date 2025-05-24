"""
Service management agent implementation.
"""
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAIAgent
from .service_metrics import ServiceMetricsCollector

class ServiceManagementAgent(BaseAIAgent):
    """AI agent for managing Open Horizon services."""
    
    def __init__(self, client):
        """Initialize the service management agent.
        
        Args:
            client: An instance of ExchangeAPIClient
        """
        super().__init__(client)
        self.metrics_collector = ServiceMetricsCollector()
        self._deployment_history = []
    
    async def analyze(self) -> Dict[str, Any]:
        """Analyze services and generate recommendations.
        
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Get all services
            services = self.client.get_services()
            if not services:
                return {
                    'services': {},
                    'recommendations': [],
                    'alerts': []
                }
            
            analysis = {
                'services': {},
                'recommendations': [],
                'alerts': []
            }
            
            # Analyze each service
            for service in services:
                service_id = service.get('id')
                if not service_id:
                    continue
                
                # Get detailed service data
                service_data = self.client.get_service(service_id)
                if not service_data:
                    continue
                
                # Collect and analyze metrics
                metrics = self.metrics_collector.collect_metrics(service_id, service_data)
                health_analysis = self.metrics_collector.analyze_metrics(service_id)
                
                # Store analysis results
                analysis['services'][service_id] = {
                    'status': health_analysis['status'],
                    'health': health_analysis['health'],
                    'metrics': health_analysis['metrics'],
                    'alerts': health_analysis['alerts']
                }
                
                # Add recommendations
                if health_analysis['recommendations']:
                    analysis['recommendations'].extend([
                        {
                            'service_id': service_id,
                            'action': self._determine_action(rec),
                            'reason': rec
                        }
                        for rec in health_analysis['recommendations']
                    ])
                
                # Add alerts
                if health_analysis['alerts']:
                    analysis['alerts'].extend([
                        {
                            'service_id': service_id,
                            'type': health_analysis['status'],
                            'message': alert
                        }
                        for alert in health_analysis['alerts']
                    ])
            
            return analysis
            
        except Exception as e:
            self._log_error(f"Service analysis failed: {str(e)}")
            return {
                'services': {},
                'recommendations': [],
                'alerts': [{
                    'type': 'error',
                    'message': f'Analysis failed: {str(e)}'
                }]
            }
    
    def _determine_action(self, recommendation: str) -> str:
        """Determine the appropriate action based on a recommendation."""
        recommendation = recommendation.lower()
        
        if 'scale' in recommendation:
            return 'scale'
        elif 'update' in recommendation:
            return 'update'
        elif 'restart' in recommendation:
            return 'restart'
        else:
            return 'investigate'
    
    async def act(self, action: Dict[str, Any]) -> bool:
        """Execute an action on a service.
        
        Args:
            action: Dictionary containing action details
            
        Returns:
            bool indicating success or failure
        """
        try:
            service_id = action.get('service_id')
            action_type = action.get('action')
            
            if not service_id or not action_type:
                self._log_error("Invalid action: missing service_id or action type")
                return False
            
            if action_type == 'scale':
                return await self._scale_service(service_id, action.get('scale_factor', 2.0))
            elif action_type == 'update':
                return await self._update_service(service_id, action.get('update_data', {}))
            elif action_type == 'restart':
                return await self._restart_service(service_id)
            else:
                self._log_error(f"Unsupported action type: {action_type}")
                return False
                
        except Exception as e:
            self._log_error(f"Action execution failed: {str(e)}")
            return False
    
    async def _update_service(self, service_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a service with new configuration."""
        try:
            org_id = self.client.org_id
            result = self.client.update_service(org_id, service_id, update_data)
            
            # Log the update
            self._deployment_history.append({
                'timestamp': datetime.now(),
                'service_id': service_id,
                'action': 'update',
                'data': update_data,
                'result': result
            })
            
            return True
        except Exception as e:
            self._log_error(f"Service update failed: {str(e)}")
            return False
    
    async def _scale_service(self, service_id: str, scale_factor: float) -> bool:
        """Scale a service up or down."""
        try:
            # Get current service data
            org_id = self.client.org_id
            service_data = self.client.get_service(service_id)
            
            # Calculate new resource requirements
            if 'deployment' in service_data and 'resources' in service_data['deployment']:
                resources = service_data['deployment']['resources']
                new_resources = {
                    'cpu': resources.get('cpu', 1.0) * scale_factor,
                    'memory': resources.get('memory', 512.0) * scale_factor
                }
                
                # Update service with new resources
                update_data = {
                    'deployment': {
                        'resources': new_resources
                    }
                }
                
                return await self._update_service(service_id, update_data)
            
            return False
            
        except Exception as e:
            self._log_error(f"Service scaling failed: {str(e)}")
            return False
    
    async def _restart_service(self, service_id: str) -> bool:
        """Restart a service."""
        try:
            # Get current service data
            org_id = self.client.org_id
            service_data = self.client.get_service(service_id)
            
            # Update service with same configuration to trigger restart
            return await self._update_service(service_id, service_data)
            
        except Exception as e:
            self._log_error(f"Service restart failed: {str(e)}")
            return False 