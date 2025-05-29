from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import os

@dataclass
class HealthCheck:
    """Represents a health check result."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    timestamp: datetime
    details: Dict[str, Any] = None

class HealthMonitor:
    """Base class for health monitoring."""
    
    def __init__(self, health_dir: str = "health"):
        self.health_dir = health_dir
        self._health_history: List[HealthCheck] = []
        self._ensure_health_dir()
    
    def _ensure_health_dir(self):
        """Ensure health directory exists."""
        if not os.path.exists(self.health_dir):
            os.makedirs(self.health_dir)
    
    def record_health_check(self, check: HealthCheck):
        """Record a health check result."""
        self._health_history.append(check)
        self._save_health_check(check)
    
    def _save_health_check(self, check: HealthCheck):
        """Save a health check result to disk."""
        timestamp = check.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.health_dir, f"health_{timestamp}.json")
        
        health_data = {
            "name": check.name,
            "status": check.status,
            "message": check.message,
            "timestamp": check.timestamp.isoformat(),
            "details": check.details or {}
        }
        
        with open(filename, 'w') as f:
            json.dump(health_data, f, indent=2)
    
    def get_health_history(self) -> List[HealthCheck]:
        """Get health check history."""
        return self._health_history.copy()
    
    def get_latest_health(self) -> Optional[HealthCheck]:
        """Get the most recent health check."""
        return self._health_history[-1] if self._health_history else None

class OrganizationHealthMonitor(HealthMonitor):
    """Monitor for organization health."""
    
    def __init__(self, health_dir: str = "health"):
        super().__init__(health_dir)
    
    async def check_organization_health(self, org_id: str, client) -> HealthCheck:
        """Check the health of an organization."""
        try:
            # Check organization access
            response = await client.get(f"/v1/orgs/{org_id}")
            if response.status_code != 200:
                return HealthCheck(
                    name="organization_access",
                    status="unhealthy",
                    message=f"Failed to access organization: {response.status_code}",
                    timestamp=datetime.now(),
                    details={"status_code": response.status_code}
                )
            
            # Check user access
            response = await client.get(f"/v1/orgs/{org_id}/users")
            if response.status_code != 200:
                return HealthCheck(
                    name="user_access",
                    status="degraded",
                    message=f"Failed to access users: {response.status_code}",
                    timestamp=datetime.now(),
                    details={"status_code": response.status_code}
                )
            
            # Check service access
            response = await client.get(f"/v1/orgs/{org_id}/services")
            if response.status_code != 200:
                return HealthCheck(
                    name="service_access",
                    status="degraded",
                    message=f"Failed to access services: {response.status_code}",
                    timestamp=datetime.now(),
                    details={"status_code": response.status_code}
                )
            
            return HealthCheck(
                name="organization_health",
                status="healthy",
                message="Organization is healthy",
                timestamp=datetime.now(),
                details={
                    "org_id": org_id,
                    "checks": ["organization_access", "user_access", "service_access"]
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="organization_health",
                status="unhealthy",
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    async def check_user_health(self, org_id: str, username: str, client) -> HealthCheck:
        """Check the health of a user."""
        try:
            # Check user access
            response = await client.get(f"/v1/orgs/{org_id}/users/{username}")
            if response.status_code != 200:
                return HealthCheck(
                    name="user_access",
                    status="unhealthy",
                    message=f"Failed to access user: {response.status_code}",
                    timestamp=datetime.now(),
                    details={"status_code": response.status_code}
                )
            
            # Check user permissions
            user_data = response.json()
            if not user_data.get("roles"):
                return HealthCheck(
                    name="user_permissions",
                    status="degraded",
                    message="User has no roles assigned",
                    timestamp=datetime.now(),
                    details={"user_data": user_data}
                )
            
            return HealthCheck(
                name="user_health",
                status="healthy",
                message="User is healthy",
                timestamp=datetime.now(),
                details={
                    "org_id": org_id,
                    "username": username,
                    "roles": user_data.get("roles", [])
                }
            )
            
        except Exception as e:
            return HealthCheck(
                name="user_health",
                status="unhealthy",
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.now(),
                details={"error": str(e)}
            )
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of health check results."""
        if not self._health_history:
            return {
                "status": "unknown",
                "message": "No health checks performed",
                "timestamp": datetime.now().isoformat()
            }
        
        # Count statuses
        status_counts = {
            "healthy": 0,
            "degraded": 0,
            "unhealthy": 0
        }
        
        for check in self._health_history:
            status_counts[check.status] += 1
        
        # Determine overall status
        if status_counts["unhealthy"] > 0:
            overall_status = "unhealthy"
        elif status_counts["degraded"] > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "counts": status_counts,
            "total_checks": len(self._health_history),
            "latest_check": self._health_history[-1].timestamp.isoformat()
        } 