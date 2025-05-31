"""
Node management agent implementation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from .base import BaseAIAgent
from .node_metrics import NodeMetricsCollector

class NodeManagementAgent(BaseAIAgent):
    """AI agent for managing Open Horizon nodes."""
    
    def __init__(self, client, config: Optional[Dict[str, Any]] = None):
        """Initialize the node management agent.
        
        Args:
            client: An instance of ExchangeAPIClient
            config: Optional configuration dictionary
        """
        super().__init__(client, config)
        self._metrics_collector = NodeMetricsCollector(config)
        self._health_history: List[Dict[str, Any]] = []
    
    async def analyze(self) -> Dict[str, Any]:
        """Analyze node health and make decisions.
        
        Returns:
            Dict containing analysis results and recommended actions
        """
        try:
            analysis = {
                'nodes': {},
                'recommendations': [],
                'alerts': []
            }
            
            # Get current nodes
            nodes = self.client.list_nodes(self.client.credential_manager._credentials.org_id)
            
            for node_id, node_data in nodes.get('nodes', {}).items():
                try:
                    # Collect metrics for the node
                    metrics = self._metrics_collector.collect_metrics(node_id, node_data)
                    metrics_analysis = self._metrics_collector.analyze_metrics(metrics)
                    
                    # Store node analysis
                    analysis['nodes'][node_id] = {
                        'status': metrics_analysis['status'],
                        'health': metrics_analysis['health'],
                        'metrics': metrics_analysis['metrics'],
                        'trends': metrics_analysis.get('trends', {})
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
                        if 'disk_usage' in metrics_analysis.get('trends', {}) and metrics_analysis['trends']['disk_usage'] == 'increasing':
                            analysis['recommendations'].append({
                                'node_id': node_id,
                                'action': 'cleanup',
                                'reason': 'Disk usage is increasing'
                            })
                            
                except Exception as e:
                    self.logger.error(f"Failed to analyze node {node_id}: {str(e)}")
                    analysis['alerts'].append({
                        'node_id': node_id,
                        'type': 'error',
                        'message': f'Analysis failed: {str(e)}'
                    })
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Node analysis failed: {str(e)}")
            return {
                'nodes': {},
                'recommendations': [],
                'alerts': [{
                    'type': 'error',
                    'message': f'Analysis failed: {str(e)}'
                }]
            }
    
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
                self.logger.error(f"Unknown action type: {action_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Action failed: {str(e)}")
            return False
    
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
            self.logger.error(f"Health check failed: {str(e)}")
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
            self.logger.error(f"Node update failed: {str(e)}")
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
                        'threshold': self.config.get('cleanup_threshold', 80)  # Start cleanup at 80% disk usage
                    }
                }
            }
            
            return await self._update_node(node_id, update_data)
            
        except Exception as e:
            self.logger.error(f"Node cleanup failed: {str(e)}")
            return False 
    
    async def register_node(self, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new node in the Exchange.
        Args:
            node_data: Dictionary containing node registration data
        Returns:
            Dict with status, node_id (if successful), and message
        """
        required_fields = ['name', 'nodeType', 'publicKey', 'token', 'registeredServices', 'policy']
        # Validate required fields
        for field in required_fields:
            if field not in node_data:
                return {
                    'status': 'error',
                    'message': f'Validation error: Missing required field: {field}'
                }
        # Validate field types
        if not isinstance(node_data['name'], str) or not isinstance(node_data['nodeType'], str):
            return {
                'status': 'error',
                'message': 'Validation error: name and nodeType must be strings.'
            }
        if not isinstance(node_data['publicKey'], str) or not isinstance(node_data['token'], str):
            return {
                'status': 'error',
                'message': 'Validation error: publicKey and token must be strings.'
            }
        if not isinstance(node_data['registeredServices'], list):
            return {
                'status': 'error',
                'message': 'Validation error: registeredServices must be a list.'
            }
        if not isinstance(node_data['policy'], dict):
            return {
                'status': 'error',
                'message': 'Validation error: policy must be a dictionary.'
            }
        try:
            org_id = self.client.credential_manager._credentials.org_id
            result = self.client.create_node(org_id, node_data)
            if result and result.get('status') == 'success':
                return {
                    'status': 'success',
                    'node_id': result.get('node_id'),
                    'message': 'Node registered successfully.'
                }
            # If API returns error details
            if result and 'error' in result:
                return {
                    'status': 'error',
                    'message': result['error']
                }
            return {
                'status': 'error',
                'message': 'Unknown error during node registration.'
            }
        except Exception as e:
            msg = str(e).lower()
            if 'already exists' in msg:
                return {
                    'status': 'error',
                    'message': f'Node already exists: {str(e)}'
                }
            if 'api' in msg:
                return {
                    'status': 'error',
                    'message': f'API error: {str(e)}'
                }
            return {
                'status': 'error',
                'message': f'Node registration failed: {str(e)}'
            }

    async def delete_node(self, node_id: str) -> Dict[str, Any]:
        """Delete a node from the Exchange.
        Args:
            node_id: ID of the node to delete
        Returns:
            Dict with status and message
        """
        if not node_id or not isinstance(node_id, str):
            return {
                'status': 'error',
                'message': 'Validation error: node_id must be a non-empty string.'
            }
        try:
            org_id = self.client.credential_manager._credentials.org_id
            result = self.client.delete_node(org_id, node_id)
            if result and result.get('status') == 'success':
                return {
                    'status': 'success',
                    'message': result.get('message', 'Node deleted successfully.')
                }
            if result and 'error' in result:
                return {
                    'status': 'error',
                    'message': result['error']
                }
            return {
                'status': 'error',
                'message': 'Unknown error during node deletion.'
            }
        except Exception as e:
            msg = str(e).lower()
            if 'not found' in msg:
                return {
                    'status': 'error',
                    'message': f'Node not found: {str(e)}'
                }
            if 'api' in msg:
                return {
                    'status': 'error',
                    'message': f'API error: {str(e)}'
                }
            if 'dependencies' in msg:
                return {
                    'status': 'error',
                    'message': f'Cannot delete node: dependencies exist. {str(e)}'
                }
            return {
                'status': 'error',
                'message': f'Node deletion failed: {str(e)}'
            }