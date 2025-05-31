"""
Organization AI Agent implementation for intelligent organization management.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from .base import BaseAIAgent
from ..organizations import OrganizationManager, OrganizationInfo, User
from ..exchange_client import ExchangeAPIClient

class OrganizationAgent(BaseAIAgent):
    """AI agent for managing and analyzing organizations."""
    
    def __init__(self, client: ExchangeAPIClient, org_manager: OrganizationManager, config: Optional[Dict[str, Any]] = None):
        """Initialize the Organization AI agent.
        
        Args:
            client: An instance of ExchangeAPIClient for API interactions
            org_manager: An instance of OrganizationManager for organization operations
            config: Optional configuration dictionary
        """
        super().__init__(client, config)
        self.org_manager = org_manager
        self._org_cache: Dict[str, OrganizationInfo] = {}
        self._user_cache: Dict[str, Dict[str, User]] = {}  # org_id -> {username -> User}
    
    async def analyze(self) -> Dict[str, Any]:
        """Analyze the current state of organizations and make decisions.
        
        Returns:
            Dict containing analysis results and recommended actions
        """
        try:
            # Get all organizations
            orgs = await self.org_manager.get_organizations()
            
            analysis_results = {
                'timestamp': self._get_timestamp(),
                'organizations': [],
                'recommendations': [],
                'alerts': []
            }
            
            for org in orgs:
                org_analysis = await self._analyze_organization(org)
                analysis_results['organizations'].append(org_analysis)
                
                # Add recommendations and alerts
                if org_analysis.get('recommendations'):
                    analysis_results['recommendations'].extend(org_analysis['recommendations'])
                if org_analysis.get('alerts'):
                    analysis_results['alerts'].extend(org_analysis['alerts'])
            
            return analysis_results
            
        except Exception as e:
            self._log_error(f"Failed to analyze organizations: {str(e)}")
            return {
                'timestamp': self._get_timestamp(),
                'error': str(e),
                'organizations': [],
                'recommendations': [],
                'alerts': [{'type': 'error', 'message': str(e)}]
            }
    
    async def act(self, action: Dict[str, Any]) -> bool:
        """Execute an action based on analysis.
        
        Args:
            action: Dictionary containing action details
            
        Returns:
            bool indicating success or failure
        """
        try:
            action_type = action.get('type')
            org_id = action.get('org_id')
            
            if not action_type or not org_id:
                raise ValueError("Action type and org_id are required")
            
            if action_type == 'update_organization':
                return await self._handle_org_update(org_id, action)
            elif action_type == 'manage_users':
                return await self._handle_user_management(org_id, action)
            elif action_type == 'health_check':
                return await self._handle_health_check(org_id)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
                
        except Exception as e:
            self._log_error(f"Failed to execute action: {str(e)}")
            return False
    
    async def _analyze_organization(self, org: OrganizationInfo) -> Dict[str, Any]:
        """Analyze a specific organization.
        
        Args:
            org: OrganizationInfo object to analyze
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Get organization health
            health = await self.org_manager.check_organization_health(org.org_id)
            
            # Get users
            users = await self.org_manager.get_users(org.org_id)
            
            # Analyze user distribution
            user_roles = {}
            for user in users:
                for role in user.roles:
                    user_roles[role] = user_roles.get(role, 0) + 1
            
            analysis = {
                'org_id': org.org_id,
                'name': org.name,
                'health': health,
                'user_distribution': user_roles,
                'recommendations': [],
                'alerts': []
            }
            
            # Generate recommendations
            if health['status'] != 'healthy':
                analysis['alerts'].append({
                    'type': 'health',
                    'message': f"Organization health check failed: {health['message']}"
                })
            
            if not user_roles.get('admin', 0):
                analysis['recommendations'].append({
                    'type': 'user_management',
                    'message': "No admin users found. Consider adding an admin user."
                })
            
            return analysis
            
        except Exception as e:
            self._log_error(f"Failed to analyze organization {org.org_id}: {str(e)}")
            return {
                'org_id': org.org_id,
                'name': org.name,
                'error': str(e),
                'recommendations': [],
                'alerts': [{'type': 'error', 'message': str(e)}]
            }
    
    async def _handle_org_update(self, org_id: str, action: Dict[str, Any]) -> bool:
        """Handle organization update action.
        
        Args:
            org_id: Organization ID
            action: Action details
            
        Returns:
            bool indicating success or failure
        """
        try:
            description = action.get('description')
            if description:
                await self.org_manager.update_organization(org_id, description)
            return True
        except Exception as e:
            self._log_error(f"Failed to update organization {org_id}: {str(e)}")
            return False
    
    async def _handle_user_management(self, org_id: str, action: Dict[str, Any]) -> bool:
        """Handle user management action.
        
        Args:
            org_id: Organization ID
            action: Action details
            
        Returns:
            bool indicating success or failure
        """
        try:
            action_subtype = action.get('subtype')
            username = action.get('username')
            roles = action.get('roles', [])
            
            if action_subtype == 'create':
                await self.org_manager.create_user(org_id, username, roles)
            elif action_subtype == 'update':
                await self.org_manager.update_user(org_id, username, roles)
            elif action_subtype == 'delete':
                await self.org_manager.delete_user(org_id, username)
            else:
                raise ValueError(f"Unknown user management action: {action_subtype}")
            
            return True
        except Exception as e:
            self._log_error(f"Failed to manage users in organization {org_id}: {str(e)}")
            return False
    
    async def _handle_health_check(self, org_id: str) -> bool:
        """Handle organization health check action.
        
        Args:
            org_id: Organization ID
            
        Returns:
            bool indicating success or failure
        """
        try:
            health = await self.org_manager.check_organization_health(org_id)
            self.update_state({
                'last_health_check': {
                    'org_id': org_id,
                    'timestamp': self._get_timestamp(),
                    'status': health['status'],
                    'message': health['message']
                }
            })
            return True
        except Exception as e:
            self._log_error(f"Failed to check health for organization {org_id}: {str(e)}")
            return False
    
    async def _process_experience(self, experience: Dict[str, Any]) -> None:
        """Process experience data for learning.
        
        Args:
            experience: Dictionary containing experience data
        """
        try:
            # Update internal state based on experience
            if 'organization_changes' in experience:
                self._org_cache.clear()
            if 'user_changes' in experience:
                self._user_cache.clear()
            
            # Log the experience
            self.logger.debug(f"Processed experience: {experience}")
            
        except Exception as e:
            self._log_error(f"Failed to process experience: {str(e)}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the agent.
        
        Returns:
            Dict containing performance metrics
        """
        base_metrics = super().get_metrics()
        base_metrics.update({
            'cached_orgs': len(self._org_cache),
            'cached_users': sum(len(users) for users in self._user_cache.values()),
            'last_health_check': self._state.get('last_health_check', {}).get('timestamp')
        })
        return base_metrics 