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