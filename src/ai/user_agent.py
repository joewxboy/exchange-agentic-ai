"""
User AI Agent implementation for intelligent user management.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from .base import BaseAIAgent
from ..organizations import OrganizationManager, User
from ..exchange_client import ExchangeAPIClient

class UserAgent(BaseAIAgent):
    """AI agent for managing and analyzing users."""
    
    def __init__(self, client: ExchangeAPIClient, org_manager: OrganizationManager, config: Optional[Dict[str, Any]] = None):
        """Initialize the User AI agent.
        
        Args:
            client: An instance of ExchangeAPIClient for API interactions
            org_manager: An instance of OrganizationManager for user operations
            config: Optional configuration dictionary
        """
        super().__init__(client, config)
        self.org_manager = org_manager
        self._user_cache: Dict[str, User] = {}  # username -> User
        self._activity_cache: Dict[str, Dict[str, Any]] = {}  # username -> activity data
    
    async def analyze(self) -> Dict[str, Any]:
        """Analyze the current state of users and make decisions.
        
        Returns:
            Dict containing analysis results and recommended actions
        """
        try:
            # Get all organizations
            orgs = await self.org_manager.get_organizations()
            
            analysis_results = {
                'timestamp': self._get_timestamp(),
                'users': [],
                'recommendations': [],
                'alerts': []
            }
            
            for org in orgs:
                # Get users for this organization
                users = await self.org_manager.get_users(org.org_id)
                
                for user in users:
                    user_analysis = await self._analyze_user(org.org_id, user)
                    analysis_results['users'].append(user_analysis)
                    
                    # Add recommendations and alerts
                    if user_analysis.get('recommendations'):
                        analysis_results['recommendations'].extend(user_analysis['recommendations'])
                    if user_analysis.get('alerts'):
                        analysis_results['alerts'].extend(user_analysis['alerts'])
            
            return analysis_results
            
        except Exception as e:
            self._log_error(f"Failed to analyze users: {str(e)}")
            return {
                'timestamp': self._get_timestamp(),
                'error': str(e),
                'users': [],
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
            username = action.get('username')
            
            if not action_type or not org_id or not username:
                raise ValueError("Action type, org_id, and username are required")
            
            if action_type == 'update_user':
                return await self._handle_user_update(org_id, username, action)
            elif action_type == 'check_health':
                return await self._handle_health_check(org_id, username)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
                
        except Exception as e:
            self._log_error(f"Failed to execute action: {str(e)}")
            return False
    
    async def _analyze_user(self, org_id: str, user: User) -> Dict[str, Any]:
        """Analyze a specific user.
        
        Args:
            org_id: Organization ID
            user: User object to analyze
            
        Returns:
            Dict containing analysis results
        """
        try:
            # Get user health
            health = await self.org_manager.check_user_health(org_id, user.username)
            
            # Analyze user roles and permissions
            role_analysis = self._analyze_user_roles(user)
            
            # Analyze user activity
            activity_analysis = self._analyze_user_activity(user)
            
            analysis = {
                'org_id': org_id,
                'username': user.username,
                'health': health,
                'roles': role_analysis,
                'activity': activity_analysis,
                'recommendations': [],
                'alerts': []
            }
            
            # Generate recommendations based on analysis
            if health['status'] != 'healthy':
                analysis['alerts'].append({
                    'type': 'health',
                    'message': f"User health check failed: {health['message']}"
                })
            
            if not user.roles:
                analysis['recommendations'].append({
                    'type': 'roles',
                    'message': "User has no roles assigned. Consider assigning appropriate roles."
                })
            
            if activity_analysis['inactivity_days'] > 30:
                analysis['recommendations'].append({
                    'type': 'activity',
                    'message': f"User has been inactive for {activity_analysis['inactivity_days']} days. Consider reaching out."
                })
            
            return analysis
            
        except Exception as e:
            self._log_error(f"Failed to analyze user {user.username}: {str(e)}")
            return {
                'org_id': org_id,
                'username': user.username,
                'error': str(e),
                'recommendations': [],
                'alerts': [{'type': 'error', 'message': str(e)}]
            }
    
    def _analyze_user_roles(self, user: User) -> Dict[str, Any]:
        """Analyze user roles and permissions.
        
        Args:
            user: User object to analyze
            
        Returns:
            Dict containing role analysis
        """
        return {
            'roles': user.roles,
            'has_admin': 'admin' in user.roles,
            'has_super_admin': 'super_admin' in user.roles,
            'role_count': len(user.roles)
        }
    
    def _analyze_user_activity(self, user: User) -> Dict[str, Any]:
        """Analyze user activity.
        
        Args:
            user: User object to analyze
            
        Returns:
            Dict containing activity analysis
        """
        try:
            last_updated = datetime.fromisoformat(user.last_updated)
            now = datetime.now()
            inactivity_days = (now - last_updated).days
            
            return {
                'last_updated': user.last_updated,
                'inactivity_days': inactivity_days,
                'is_active': inactivity_days <= 7,  # Consider active if updated in last 7 days
                'activity_level': 'high' if inactivity_days <= 1 else 'medium' if inactivity_days <= 7 else 'low'
            }
        except Exception as e:
            self._log_error(f"Failed to analyze user activity: {str(e)}")
            return {
                'last_updated': user.last_updated,
                'inactivity_days': None,
                'is_active': None,
                'activity_level': 'unknown'
            }
    
    async def _handle_user_update(self, org_id: str, username: str, action: Dict[str, Any]) -> bool:
        """Handle user update action.
        
        Args:
            org_id: Organization ID
            username: Username
            action: Action details
            
        Returns:
            bool indicating success or failure
        """
        try:
            roles = action.get('roles')
            if roles:
                await self.org_manager.update_user(org_id, username, roles)
            return True
        except Exception as e:
            self._log_error(f"Failed to update user {username}: {str(e)}")
            return False
    
    async def _handle_health_check(self, org_id: str, username: str) -> bool:
        """Handle user health check action.
        
        Args:
            org_id: Organization ID
            username: Username
            
        Returns:
            bool indicating success or failure
        """
        try:
            health = await self.org_manager.check_user_health(org_id, username)
            self.update_state({
                'last_health_check': {
                    'org_id': org_id,
                    'username': username,
                    'timestamp': self._get_timestamp(),
                    'status': health['status'],
                    'message': health['message']
                }
            })
            return True
        except Exception as e:
            self._log_error(f"Failed to check health for user {username}: {str(e)}")
            return False
    
    async def _process_experience(self, experience: Dict[str, Any]) -> None:
        """Process experience data for learning.
        
        Args:
            experience: Dictionary containing experience data
        """
        try:
            # Update internal state based on experience
            if 'user_changes' in experience:
                self._user_cache.clear()
            if 'activity_changes' in experience:
                self._activity_cache.clear()
            
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
            'cached_users': len(self._user_cache),
            'cached_activities': len(self._activity_cache),
            'last_health_check': self._state.get('last_health_check', {}).get('timestamp')
        })
        return base_metrics 