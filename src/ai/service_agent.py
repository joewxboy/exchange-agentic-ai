"""
Service Management Agent implementation.
"""
from typing import Dict, Any, List
import pandas as pd
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish
from .base import BaseAIAgent
from .service_metrics import ServiceMetricsCollector

class ServiceManagementAgent(BaseAIAgent):
    """AI agent for managing Open Horizon services."""
    
    def __init__(self, client):
        """Initialize the service management agent.
        
        Args:
            client: An instance of ExchangeAPIClient
        """
        super().__init__(client)
        self._metrics_collector = ServiceMetricsCollector(client)
        self._deployment_history: List[Dict[str, Any]] = []
        self.tools = self._create_tools()
        self.agent = self._create_agent()
    
    def _create_tools(self) -> List[Tool]:
        """Create tools for the agent."""
        return [
            Tool(
                name="get_service_metrics",
                func=self._get_service_metrics,
                description="Get metrics for a specific service"
            ),
            Tool(
                name="analyze_service_health",
                func=self._analyze_service_health,
                description="Analyze the health of a service based on its metrics"
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent executor."""
        # This is a placeholder - in a real implementation, you would use a proper LLM
        return None
    
    def _get_service_metrics(self, service_id: str) -> Dict[str, Any]:
        """Get metrics for a service."""
        return self._metrics_collector.collect_service_metrics(service_id)
    
    def _analyze_service_health(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze service health based on metrics."""
        return self._metrics_collector.analyze_service_health(metrics)
    
    def analyze_service(self, service_id: str) -> Dict[str, Any]:
        """Analyze a service and provide recommendations."""
        metrics = self._get_service_metrics(service_id)
        return self._analyze_service_health(metrics)
    
    async def analyze(self) -> Dict[str, Any]:
        """Analyze service health and make decisions.
        
        Returns:
            Dict containing analysis results and recommended actions
        """
        analysis = {
            'services': {},
            'recommendations': [],
            'alerts': []
        }
        
        # Get current services
        services = self.client.list_services(self.client.credential_manager._credentials.org_id)
        
        for service_id, service_data in services.get('services', {}).items():
            # Collect metrics for the service
            metrics = self._collect_service_metrics(service_id, service_data)
            self._metrics_collector.add_metrics(metrics)
            
            # Get recent metrics and analyze
            recent_metrics = self._metrics_collector.get_recent_metrics()
            metrics_analysis = self._metrics_collector.analyze_metrics(recent_metrics)
            
            # Store service analysis
            analysis['services'][service_id] = {
                'status': metrics_analysis['status'],
                'health': metrics_analysis['health'],
                'metrics': metrics_analysis['statistics'],
                'trends': metrics_analysis['trends']
            }
            
            # Add alerts
            analysis['alerts'].extend(metrics_analysis['alerts'])
            
            # Generate recommendations based on analysis
            if metrics_analysis['status'] == 'failed':
                analysis['recommendations'].append({
                    'service_id': service_id,
                    'action': 'restart',
                    'reason': 'Service has failed'
                })
            elif metrics_analysis['health'] == 'critical':
                analysis['recommendations'].append({
                    'service_id': service_id,
                    'action': 'update',
                    'reason': 'Service health is critical'
                })
            elif metrics_analysis['health'] == 'warning':
                if 'cpu_usage' in metrics_analysis['trends'] and metrics_analysis['trends']['cpu_usage'] == 'increasing':
                    analysis['recommendations'].append({
                        'service_id': service_id,
                        'action': 'scale',
                        'reason': 'CPU usage is increasing'
                    })
        
        return analysis
    
    async def act(self, action: Dict[str, Any]) -> bool:
        """Execute a service management action.
        
        Args:
            action: Dictionary containing action details
            
        Returns:
            bool indicating success or failure
        """
        try:
            service_id = action['service_id']
            action_type = action['action']
            
            if action_type == 'update':
                return await self._update_service(service_id, action.get('update_data', {}))
            elif action_type == 'scale':
                return await self._scale_service(service_id, action.get('scale_factor', 1))
            elif action_type == 'restart':
                return await self._restart_service(service_id)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
                
        except Exception as e:
            self._log_error(f"Action failed: {str(e)}")
            return False
    
    def _collect_service_metrics(self, service_id: str, service_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics for a service.
        
        Args:
            service_id: ID of the service
            service_data: Service data from the API
            
        Returns:
            Dictionary containing service metrics
        """
        metrics = {
            'service_id': service_id,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'error_rate': 0.0,
            'response_time': 0.0
        }
        
        # Extract metrics from service data
        if 'deployment' in service_data:
            deployment = service_data['deployment']
            if 'resources' in deployment:
                resources = deployment['resources']
                metrics['cpu_usage'] = resources.get('cpu', 0.0)
                metrics['memory_usage'] = resources.get('memory', 0.0)
        
        # Add any additional metrics from service data
        if 'metrics' in service_data:
            metrics.update(service_data['metrics'])
        
        return metrics
    
    async def _update_service(self, service_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a service with new configuration.
        
        Args:
            service_id: ID of the service to update
            update_data: New configuration data
            
        Returns:
            bool indicating success or failure
        """
        try:
            org_id = self.client.credential_manager._credentials.org_id
            result = self.client.update_service(org_id, service_id, update_data)
            
            # Log the update
            self._deployment_history.append({
                'timestamp': self._get_timestamp(),
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
        """Scale a service up or down.
        
        Args:
            service_id: ID of the service to scale
            scale_factor: Factor to scale by (e.g., 2.0 for double)
            
        Returns:
            bool indicating success or failure
        """
        try:
            # Get current service data
            org_id = self.client.credential_manager._credentials.org_id
            service_data = self.client.get_service(org_id, service_id)
            
            # Calculate new resource requirements
            new_resources = self._calculate_scaled_resources(
                service_data.get('deployment', {}),
                scale_factor
            )
            
            # Update service with new resources
            update_data = {
                'deployment': new_resources
            }
            
            return await self._update_service(service_id, update_data)
            
        except Exception as e:
            self._log_error(f"Service scaling failed: {str(e)}")
            return False
    
    async def _restart_service(self, service_id: str) -> bool:
        """Restart a service.
        
        Args:
            service_id: ID of the service to restart
            
        Returns:
            bool indicating success or failure
        """
        try:
            # Get current service data
            org_id = self.client.credential_manager._credentials.org_id
            service_data = self.client.get_service(org_id, service_id)
            
            # Update service with same configuration to trigger restart
            return await self._update_service(service_id, service_data)
            
        except Exception as e:
            self._log_error(f"Service restart failed: {str(e)}")
            return False
    
    def _calculate_scaled_resources(self, deployment: Dict[str, Any], scale_factor: float) -> Dict[str, Any]:
        """Calculate new resource requirements for scaling.
        
        Args:
            deployment: Current deployment configuration
            scale_factor: Factor to scale by
            
        Returns:
            Dict: New deployment configuration
        """
        if 'resources' not in deployment:
            return deployment
        
        resources = deployment['resources'].copy()
        
        # Scale numeric resources
        for key in ['cpu', 'memory']:
            if key in resources and isinstance(resources[key], (int, float)):
                resources[key] = resources[key] * scale_factor
        
        deployment['resources'] = resources
        return deployment
    
    def _log_error(self, error_message: str) -> None:
        """Log an error message.
        
        Args:
            error_message: Error message to log
        """
        self._history.append({
            'timestamp': self._get_timestamp(),
            'type': 'error',
            'message': error_message
        }) 