"""
Organization metrics collection and analysis implementation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np
from .metrics import BaseMetricsCollector
from ..organizations import OrganizationInfo, User

class OrganizationMetricsCollector(BaseMetricsCollector):
    """Collector for organization-related metrics."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the organization metrics collector.
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config)
        self._health_thresholds = {
            'user_count': {'warning': 5, 'critical': 1},
            'admin_ratio': {'warning': 0.1, 'critical': 0.05},
            'activity_score': {'warning': 0.5, 'critical': 0.2}
        }
    
    def _collect_entity_metrics(self, entity_id: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metrics for an organization.
        
        Args:
            entity_id: Organization ID
            entity_data: Organization data
            
        Returns:
            Dictionary containing collected metrics
        """
        try:
            org_info = entity_data.get('info')
            users = entity_data.get('users', [])
            health = entity_data.get('health', {})
            
            if not org_info or not isinstance(org_info, OrganizationInfo):
                raise ValueError("Invalid organization info")
            
            # Calculate basic metrics
            total_users = len(users)
            admin_users = sum(1 for user in users if 'admin' in user.roles)
            super_admin_users = sum(1 for user in users if 'super_admin' in user.roles)
            
            # Calculate derived metrics
            admin_ratio = admin_users / total_users if total_users > 0 else 0
            super_admin_ratio = super_admin_users / total_users if total_users > 0 else 0
            
            # Calculate activity score based on last_updated timestamps
            now = datetime.now()
            user_activity_scores = []
            for user in users:
                if hasattr(user, 'last_updated'):
                    last_updated = datetime.fromisoformat(user.last_updated)
                    days_since_update = (now - last_updated).days
                    activity_score = 1.0 / (1.0 + days_since_update)  # Decay function
                    user_activity_scores.append(activity_score)
            
            avg_activity_score = np.mean(user_activity_scores) if user_activity_scores else 0
            
            metrics = {
                'org_id': entity_id,
                'name': org_info.name,
                'total_users': total_users,
                'admin_users': admin_users,
                'super_admin_users': super_admin_users,
                'admin_ratio': admin_ratio,
                'super_admin_ratio': super_admin_ratio,
                'activity_score': avg_activity_score,
                'health_status': health.get('status', 'unknown'),
                'health_message': health.get('message', ''),
                'created_at': org_info.created,
                'last_updated': org_info.last_updated
            }
            
            return metrics
            
        except Exception as e:
            self._log_error(f"Failed to collect metrics for organization {entity_id}: {str(e)}")
            return {
                'org_id': entity_id,
                'error': str(e),
                'timestamp': datetime.now()
            }
    
    def _analyze_entity_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze organization metrics and provide insights.
        
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
            
            # Check user count
            if metrics['total_users'] <= self._health_thresholds['user_count']['critical']:
                analysis['status'] = 'critical'
                analysis['alerts'].append({
                    'type': 'user_count',
                    'level': 'critical',
                    'message': f"Organization has critically low user count: {metrics['total_users']}"
                })
            elif metrics['total_users'] <= self._health_thresholds['user_count']['warning']:
                analysis['status'] = 'warning'
                analysis['alerts'].append({
                    'type': 'user_count',
                    'level': 'warning',
                    'message': f"Organization has low user count: {metrics['total_users']}"
                })
            
            # Check admin ratio
            if metrics['admin_ratio'] <= self._health_thresholds['admin_ratio']['critical']:
                analysis['status'] = 'critical'
                analysis['alerts'].append({
                    'type': 'admin_ratio',
                    'level': 'critical',
                    'message': f"Critical admin ratio: {metrics['admin_ratio']:.2%}"
                })
            elif metrics['admin_ratio'] <= self._health_thresholds['admin_ratio']['warning']:
                analysis['status'] = 'warning'
                analysis['alerts'].append({
                    'type': 'admin_ratio',
                    'level': 'warning',
                    'message': f"Low admin ratio: {metrics['admin_ratio']:.2%}"
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
            if metrics['admin_ratio'] < 0.1:
                analysis['recommendations'].append({
                    'type': 'user_management',
                    'priority': 'high',
                    'message': "Consider adding more admin users to improve management capabilities"
                })
            
            if metrics['activity_score'] < 0.5:
                analysis['recommendations'].append({
                    'type': 'engagement',
                    'priority': 'medium',
                    'message': "Consider implementing user engagement initiatives"
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
    
    def get_trend_analysis(self, org_id: str, window_days: int = 30) -> Dict[str, Any]:
        """Get trend analysis for an organization.
        
        Args:
            org_id: Organization ID
            window_days: Number of days to analyze
            
        Returns:
            Dictionary containing trend analysis
        """
        try:
            # Get metrics history for the organization
            metrics_history = self.get_metrics_history(window_days * 24 * 60)  # Convert days to minutes
            org_metrics = [m for m in metrics_history if m.get('org_id') == org_id]
            
            if not org_metrics:
                return {
                    'status': 'no_data',
                    'message': f"No metrics data available for the last {window_days} days"
                }
            
            # Convert to DataFrame for analysis
            df = pd.DataFrame(org_metrics)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Calculate trends
            trends = {
                'user_growth': self._calculate_growth_rate(df, 'total_users'),
                'admin_ratio_trend': self._calculate_trend(df, 'admin_ratio'),
                'activity_trend': self._calculate_trend(df, 'activity_score'),
                'health_trend': self._calculate_health_trend(df)
            }
            
            return {
                'status': 'success',
                'trends': trends,
                'summary': self._generate_trend_summary(trends)
            }
            
        except Exception as e:
            self._log_error(f"Failed to get trend analysis for organization {org_id}: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _calculate_growth_rate(self, df: pd.DataFrame, column: str) -> float:
        """Calculate growth rate for a metric.
        
        Args:
            df: DataFrame containing metrics
            column: Column to calculate growth rate for
            
        Returns:
            float: Growth rate
        """
        if len(df) < 2:
            return 0.0
        
        first_value = df[column].iloc[0]
        last_value = df[column].iloc[-1]
        
        if first_value == 0:
            return 0.0
        
        return (last_value - first_value) / first_value
    
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
        
        # User growth summary
        if trends['user_growth'] > 0.1:
            summary.append({
                'type': 'positive',
                'metric': 'user_growth',
                'message': f"Strong user growth: {trends['user_growth']:.1%}"
            })
        elif trends['user_growth'] < -0.1:
            summary.append({
                'type': 'negative',
                'metric': 'user_growth',
                'message': f"Declining user base: {trends['user_growth']:.1%}"
            })
        
        # Admin ratio trend summary
        if trends['admin_ratio_trend'] > 0:
            summary.append({
                'type': 'positive',
                'metric': 'admin_ratio',
                'message': "Improving admin ratio"
            })
        elif trends['admin_ratio_trend'] < 0:
            summary.append({
                'type': 'negative',
                'metric': 'admin_ratio',
                'message': "Declining admin ratio"
            })
        
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
        
        return summary 