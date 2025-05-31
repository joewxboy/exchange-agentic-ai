"""
User metrics collection and analysis implementation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np
from .metrics import BaseMetricsCollector
from ..organizations import User

class UserMetricsCollector(BaseMetricsCollector):
    """Collector for user-related metrics."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the user metrics collector.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._health_thresholds = {
            'inactivity_days': {'warning': 7, 'critical': 30},
            'role_count': {'warning': 1, 'critical': 0},
            'activity_score': {'warning': 0.5, 'critical': 0.2}
        }
    
    def _collect_entity_metrics(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics for a user.
        
        Args:
            entity_id: User ID (username)
            entity_data: User data
            
        Returns:
            Dictionary containing collected metrics
        """
        try:
            user = entity_data.get('user')
            health = entity_data.get('health', {})
            
            if not user or not isinstance(user, User):
                raise ValueError("Invalid user data")
            
            # Calculate basic metrics
            role_count = len(user.roles)
            has_admin = 'admin' in user.roles
            has_super_admin = 'super_admin' in user.roles
            
            # Calculate activity metrics
            last_updated = datetime.fromisoformat(user.last_updated)
            now = datetime.now()
            inactivity_days = (now - last_updated).days
            activity_score = 1.0 / (1.0 + inactivity_days)  # Decay function
            
            metrics = {
                'username': entity_id,
                'org_id': user.org_id,
                'role_count': role_count,
                'has_admin': has_admin,
                'has_super_admin': has_super_admin,
                'inactivity_days': inactivity_days,
                'activity_score': activity_score,
                'health_status': health.get('status', 'unknown'),
                'health_message': health.get('message', ''),
                'created_at': user.created,
                'last_updated': user.last_updated
            }
            
            return metrics
            
        except Exception as e:
            self._log_error(f"Failed to collect metrics for user {entity_id}: {str(e)}")
            return {
                'username': entity_id,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def _analyze_entity_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze user metrics and provide insights.
        
        Args:
            metrics: Dictionary containing metric values
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            analysis = {
                'status': 'healthy',
                'health': 'good',
                'alerts': [],
                'recommendations': []
            }
            
            # Check inactivity
            if metrics['inactivity_days'] >= self._health_thresholds['inactivity_days']['critical']:
                analysis['status'] = 'critical'
                analysis['alerts'].append({
                    'type': 'inactivity',
                    'level': 'critical',
                    'message': f"User has been inactive for {metrics['inactivity_days']} days"
                })
            elif metrics['inactivity_days'] >= self._health_thresholds['inactivity_days']['warning']:
                analysis['status'] = 'warning'
                analysis['alerts'].append({
                    'type': 'inactivity',
                    'level': 'warning',
                    'message': f"User has been inactive for {metrics['inactivity_days']} days"
                })
            
            # Check role count
            if metrics['role_count'] <= self._health_thresholds['role_count']['critical']:
                analysis['status'] = 'critical'
                analysis['alerts'].append({
                    'type': 'roles',
                    'level': 'critical',
                    'message': "User has no roles assigned"
                })
            elif metrics['role_count'] <= self._health_thresholds['role_count']['warning']:
                analysis['status'] = 'warning'
                analysis['alerts'].append({
                    'type': 'roles',
                    'level': 'warning',
                    'message': f"User has only {metrics['role_count']} role(s) assigned"
                })
            
            # Check activity score
            if metrics['activity_score'] <= self._health_thresholds['activity_score']['critical']:
                analysis['status'] = 'critical'
                analysis['alerts'].append({
                    'type': 'activity',
                    'level': 'critical',
                    'message': f"Critical activity score: {metrics['activity_score']:.2f}"
                })
            elif metrics['activity_score'] <= self._health_thresholds['activity_score']['warning']:
                analysis['status'] = 'warning'
                analysis['alerts'].append({
                    'type': 'activity',
                    'level': 'warning',
                    'message': f"Low activity score: {metrics['activity_score']:.2f}"
                })
            
            # Generate recommendations based on analysis
            if metrics['role_count'] == 0:
                analysis['recommendations'].append({
                    'type': 'roles',
                    'priority': 'high',
                    'message': "Assign appropriate roles to the user"
                })
            
            if metrics['inactivity_days'] > 7:
                analysis['recommendations'].append({
                    'type': 'engagement',
                    'priority': 'medium',
                    'message': "Consider reaching out to the user to understand their needs"
                })
            
            # Set overall health status
            if analysis['status'] == 'critical':
                analysis['health'] = 'critical'
            elif analysis['status'] == 'warning':
                analysis['health'] = 'warning'
            else:
                analysis['health'] = 'good'
            
            return analysis
            
        except Exception as e:
            self._log_error(f"Failed to analyze metrics: {str(e)}")
            return {
                'status': 'unknown',
                'health': 'unknown',
                'alerts': [{'type': 'error', 'message': str(e)}],
                'recommendations': []
            }
    
    def get_trend_analysis(self, username: str, window_days: int = 30) -> Dict[str, Any]:
        """Get trend analysis for a user.
        
        Args:
            username: Username
            window_days: Number of days to analyze
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            # Get metrics history for the user
            metrics_history = self.get_metrics_history(window_days * 24 * 60)  # Convert days to minutes
            user_metrics = [m for m in metrics_history if m.get('username') == username]
            
            if not user_metrics:
                return {
                    'status': 'no_data',
                    'message': f"No metrics data available for the last {window_days} days"
                }
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(user_metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate trends
            trends = {
                'activity_trend': self._calculate_trend(df, 'activity_score'),
                'inactivity_trend': self._calculate_trend(df, 'inactivity_days'),
                'health_trend': self._calculate_health_trend(df)
            }
            
            return {
                'status': 'success',
                'trends': trends,
                'summary': self._generate_trend_summary(trends)
            }
            
        except Exception as e:
            self._log_error(f"Failed to get trend analysis for user {username}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _calculate_trend(self, df: pd.DataFrame, column: str) -> float:
        """Calculate trend for a metric using linear regression.
        
        Args:
            df: DataFrame containing metrics
            column: Column to calculate trend for
            
        Returns:
            float: Trend coefficient
        """
        if len(df) < 2:
            return 0.0
        
        x = np.arange(len(df))
        y = df[column].values
        
        slope, _ = np.polyfit(x, y, 1)
        return slope
    
    def _calculate_health_trend(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate health trend metrics.
        
        Args:
            df: DataFrame containing metrics
            
        Returns:
            Dict containing health trend metrics
        """
        if len(df) < 2:
            return {'status': 'no_data'}
        
        # Calculate percentage of time in each health state
        health_states = df['health_status'].value_counts(normalize=True)
        
        return {
            'healthy_ratio': health_states.get('healthy', 0),
            'warning_ratio': health_states.get('warning', 0),
            'critical_ratio': health_states.get('critical', 0)
        }
    
    def _generate_trend_summary(self, trends: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate summary of trends.
        
        Args:
            trends: Dictionary containing trend metrics
            
        Returns:
            List of trend summaries
        """
        summary = []
        
        # Activity trend summary
        if trends['activity_trend'] > 0:
            summary.append({
                'type': 'positive',
                'metric': 'activity',
                'message': "Increasing user activity"
            })
        elif trends['activity_trend'] < 0:
            summary.append({
                'type': 'negative',
                'metric': 'activity',
                'message': "Decreasing user activity"
            })
        
        # Inactivity trend summary
        if trends['inactivity_trend'] > 0:
            summary.append({
                'type': 'negative',
                'metric': 'inactivity',
                'message': "Increasing user inactivity"
            })
        elif trends['inactivity_trend'] < 0:
            summary.append({
                'type': 'positive',
                'metric': 'inactivity',
                'message': "Decreasing user inactivity"
            })
        
        return summary 