from typing import Dict, Any, List
from .base import BaseAIAgent
from .node_metrics import NodeMetricsCollector

class NodeManagementAgent(BaseAIAgent):
    """AI agent for managing Open Horizon nodes."""
    
    def __init__(self, client):
        """Initialize the node management agent.
        
        Args:
            client: An instance of ExchangeAPIClient
        """
        super().__init__(client)
        self._metrics_collector = NodeMetricsCollector()
        self._health_history: List[Dict[str, Any]] = []
    
    async def analyze(self) -> Dict[str, Any]:
        """Analyze node health and make decisions.
        
        Returns:
            Dict containing analysis results and recommended actions
        """
        analysis = {
            'nodes': {},
            'recommendations': [],
            'alerts': []
        }
        
        # Get current nodes
        nodes = self.client.list_nodes(self.client.credential_manager._credentials.org_id)
        
        for node_id, node_data in nodes.get('nodes', {}).items():
            # Collect metrics for the node
            metrics = self._collect_node_metrics(node_id, node_data)
            self._metrics_collector.add_metrics(metrics)
            
            # Get recent metrics and analyze
            recent_metrics = self._metrics_collector.get_recent_metrics()
            metrics_analysis = self._metrics_collector.analyze_metrics(recent_metrics)
            
            # Store node analysis
            analysis['nodes'][node_id] = {
                'status': metrics_analysis['status'],
                'health': metrics_analysis['health'],
                'metrics': metrics_analysis['statistics'],
                'trends': metrics_analysis['trends']
            }
            
            # Add alerts
            analysis['alerts'].extend(metrics_analysis['alerts'])
            
            # Generate recommendations based on analysis
            if metrics_analysis['status'] == 'offline':
                analysis['recommendations'].append({
                    'node_id': node_id,
                    'action': 'check_health',
                    'reason': 'Node is offline'
                })
            elif metrics_analysis['health'] == 'critical':
                analysis['recommendations'].append({
                    'node_id': node_id,
                    'action': 'update',
                    'reason': 'Node health is critical'
                })
            elif metrics_analysis['health'] == 'warning':
                if 'disk_usage' in metrics_analysis['trends'] and metrics_analysis['trends']['disk_usage'] == 'increasing':
                    analysis['recommendations'].append({
                        'node_id': node_id,
                        'action': 'cleanup',
                        'reason': 'Disk usage is increasing'
                    })
        
        return analysis
    
    async def act(self, action: Dict[str, Any]) -> bool:
        """Execute a node management action.
        
        Args:
            action: Dictionary containing action details
            
        Returns:
            bool indicating success or failure
        """
        try:
            node_id = action['node_id']
            action_type = action['action']
            
            if action_type == 'check_health':
                return await self._check_node_health(node_id)
            elif action_type == 'update':
                return await self._update_node(node_id, action.get('update_data', {}))
            elif action_type == 'cleanup':
                return await self._cleanup_node(node_id)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
                
        except Exception as e:
            self._log_error(f"Action failed: {str(e)}")
            return False
    
    def _collect_node_metrics(self, node_id: str, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics for a node.
        
        Args:
            node_id: ID of the node
            node_data: Node data from the API
            
        Returns:
            Dictionary containing node metrics
        """
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
    
    async def _check_node_health(self, node_id: str) -> bool:
        """Check the health of a node.
        
        Args:
            node_id: ID of the node to check
            
        Returns:
            bool indicating success or failure
        """
        try:
            org_id = self.client.credential_manager._credentials.org_id
            node_data = self.client.get_node(org_id, node_id)
            
            # Log the health check
            self._health_history.append({
                'timestamp': self._get_timestamp(),
                'node_id': node_id,
                'status': node_data.get('status', 'unknown'),
                'last_heartbeat': node_data.get('lastHeartbeat', 'unknown')
            })
            
            return True
        except Exception as e:
            self._log_error(f"Health check failed: {str(e)}")
            return False
    
    async def _update_node(self, node_id: str, update_data: Dict[str, Any]) -> bool:
        """Update a node with new configuration.
        
        Args:
            node_id: ID of the node to update
            update_data: New configuration data
            
        Returns:
            bool indicating success or failure
        """
        try:
            org_id = self.client.credential_manager._credentials.org_id
            result = self.client.update_node(org_id, node_id, update_data)
            
            # Log the update
            self._history.append({
                'timestamp': self._get_timestamp(),
                'node_id': node_id,
                'action': 'update',
                'data': update_data,
                'result': result
            })
            
            return True
        except Exception as e:
            self._log_error(f"Node update failed: {str(e)}")
            return False
    
    async def _cleanup_node(self, node_id: str) -> bool:
        """Clean up a node's disk space.
        
        Args:
            node_id: ID of the node to clean up
            
        Returns:
            bool indicating success or failure
        """
        try:
            # Get current node data
            org_id = self.client.credential_manager._credentials.org_id
            node_data = self.client.get_node(org_id, node_id)
            
            # Add cleanup configuration
            update_data = {
                'status': {
                    'cleanup': {
                        'enabled': True,
                        'threshold': 80  # Start cleanup at 80% disk usage
                    }
                }
            }
            
            return await self._update_node(node_id, update_data)
            
        except Exception as e:
            self._log_error(f"Node cleanup failed: {str(e)}")
            return False
    
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