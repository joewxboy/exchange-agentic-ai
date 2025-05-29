from typing import List, Dict, Optional, Union, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import time
import json
import os
from src.exchange_client import ExchangeAPIClient
from src.exceptions import ExchangeAPIError
from src.validation import (
    validate_organization_data,
    validate_user_data,
    validate_permission_level,
    OrganizationValidationError,
    UserValidationError,
    PermissionValidationError
)
from src.metrics import OrganizationMetricsCollector
from src.health import OrganizationHealthMonitor
from enum import Enum

class PermissionError(ExchangeAPIError):
    """Raised when the user lacks the necessary permissions for an operation."""
    def __init__(self, message: str, required_permission: Optional[str] = None):
        self.required_permission = required_permission
        super().__init__(message)

class CacheEntry:
    """Represents a cache entry with expiration."""
    def __init__(self, data: any, ttl: int = 300):
        self.data = data
        self.created_at = datetime.now()
        self.ttl = ttl

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)

class PermissionLevel(Enum):
    USER = "user"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

    @classmethod
    def from_roles(cls, roles: List[str]) -> 'PermissionLevel':
        if "super_admin" in roles:
            return cls.SUPER_ADMIN
        elif "admin" in roles:
            return cls.ADMIN
        return cls.USER

    def can_perform(self, required_permission: 'PermissionLevel') -> bool:
        order = [PermissionLevel.USER, PermissionLevel.ADMIN, PermissionLevel.SUPER_ADMIN]
        return order.index(self) >= order.index(required_permission)

class OrganizationInfo(BaseModel):
    """Model for organization information."""
    org_id: str
    name: str
    description: Optional[str]
    created: str
    last_updated: str

class User(BaseModel):
    """Model for user information."""
    username: str
    org_id: str
    roles: List[str]
    created: str
    last_updated: str

class OrganizationManager:
    """Class for managing organizations and users."""
    
    def __init__(self, client: ExchangeAPIClient, cache_ttl: int = 300, metrics_dir: str = "metrics", health_dir: str = "health"):
        self.client = client
        self.metrics = OrganizationMetricsCollector(metrics_dir)
        self.health = OrganizationHealthMonitor(health_dir)
        self._cache: Dict[str, CacheEntry] = {}
        self._cache_ttl = cache_ttl

    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate a cache key from prefix and arguments."""
        return f"{prefix}:{':'.join(str(arg) for arg in args)}"

    def _get_from_cache(self, key: str) -> Optional[any]:
        """Get data from cache if it exists and is not expired."""
        if key in self._cache:
            entry = self._cache[key]
            if not entry.is_expired():
                self.metrics.record_cache_hit()
                return entry.data
            del self._cache[key]
        self.metrics.record_cache_miss()
        return None

    def _set_cache(self, key: str, data: any) -> None:
        """Store data in cache with TTL."""
        self._cache[key] = CacheEntry(data, self._cache_ttl)

    def _invalidate_cache(self, prefix: str) -> None:
        """Invalidate all cache entries with the given prefix."""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(prefix)]
        for key in keys_to_remove:
            del self._cache[key]

    async def get_organizations(self) -> List[OrganizationInfo]:
        """Get all organizations the user has access to."""
        start_time = time.time()
        cache_key = self._get_cache_key("orgs")
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.client.get(f"/v1/orgs")
            if response.status_code == 403:
                self.metrics.record_error("permission_error")
                raise PermissionError(
                    "Insufficient permissions to view organizations",
                    required_permission="view_orgs"
                )
            result = [OrganizationInfo(**org) for org in response.json()]
            self._set_cache(cache_key, result)
            self.metrics.record_organization_operation("get_all", True)
            self.metrics.record_response_time("get_organizations", time.time() - start_time)
            return result
        except Exception as e:
            self.metrics.record_organization_operation("get_all", False)
            self.metrics.record_error("api_error")
            raise ExchangeAPIError(f"Failed to get organizations: {str(e)}")

    async def get_organization(self, org_id: str) -> OrganizationInfo:
        """Get detailed information about a specific organization."""
        cache_key = self._get_cache_key("org", org_id)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.client.get(f"/v1/orgs/{org_id}")
            result = OrganizationInfo(**response.json())
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            raise ExchangeAPIError(f"Failed to get organization {org_id}: {str(e)}")

    async def create_organization(self, name: str, description: Optional[str] = None) -> OrganizationInfo:
        """Create a new organization. Requires super_admin or admin permissions."""
        start_time = time.time()
        try:
            # Validate organization data
            org_data = {
                "name": name,
                "description": description,
                "org_id": "temp"  # Will be replaced by server
            }
            validate_organization_data(org_data)

            response = await self.client.post(f"/v1/orgs", json={
                "name": name,
                "description": description
            })
            if response.status_code == 403:
                self.metrics.record_error("permission_error")
                raise PermissionError(
                    "Insufficient permissions to create organizations",
                    required_permission="create_orgs"
                )
            result = OrganizationInfo(**response.json())
            self._invalidate_cache("orgs")
            self.metrics.record_organization_operation("create", True)
            self.metrics.record_response_time("create_organization", time.time() - start_time)
            return result
        except (OrganizationValidationError, PermissionError) as e:
            self.metrics.record_organization_operation("create", False)
            self.metrics.record_error("validation_error" if isinstance(e, OrganizationValidationError) else "permission_error")
            raise e
        except Exception as e:
            self.metrics.record_organization_operation("create", False)
            self.metrics.record_error("api_error")
            raise ExchangeAPIError(f"Failed to create organization: {str(e)}")

    async def update_organization(self, org_id: str, description: str) -> OrganizationInfo:
        """Update organization information."""
        try:
            # Validate organization data
            org_data = {
                "name": "temp",  # Not being updated
                "description": description,
                "org_id": org_id
            }
            validate_organization_data(org_data)

            data = {
                "description": description
            }
            response = await self.client.put(f"/v1/orgs/{org_id}", json=data)
            result = OrganizationInfo(**response.json())
            self._invalidate_cache("orgs")
            self._invalidate_cache(f"org:{org_id}")
            return result
        except OrganizationValidationError as e:
            raise e
        except Exception as e:
            raise ExchangeAPIError(f"Failed to update organization {org_id}: {str(e)}")

    async def delete_organization(self, org_id: str) -> None:
        """Delete an organization. Requires super_admin permissions."""
        try:
            response = await self.client.delete(f"/v1/orgs/{org_id}")
            if response.status_code == 403:
                raise PermissionError(
                    f"Insufficient permissions to delete organization {org_id}",
                    required_permission="delete_orgs"
                )
            self._invalidate_cache("orgs")
            self._invalidate_cache(f"org:{org_id}")
        except Exception as e:
            raise ExchangeAPIError(f"Failed to delete organization {org_id}: {str(e)}")

    async def get_users(self, org_id: str) -> List[User]:
        """Get all users in an organization."""
        cache_key = self._get_cache_key("users", org_id)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.client.get(f"/v1/orgs/{org_id}/users")
            result = [User(**user) for user in response.json()]
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            raise ExchangeAPIError(f"Failed to get users for organization {org_id}: {str(e)}")

    async def get_user(self, org_id: str, username: str) -> User:
        """Get detailed information about a specific user."""
        cache_key = self._get_cache_key("user", org_id, username)
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            response = await self.client.get(f"/v1/orgs/{org_id}/users/{username}")
            result = User(**response.json())
            self._set_cache(cache_key, result)
            return result
        except Exception as e:
            raise ExchangeAPIError(f"Failed to get user {username} in organization {org_id}: {str(e)}")

    async def create_user(self, org_id: str, username: str, roles: List[str]) -> User:
        """Create a new user in an organization. Requires admin or super_admin permissions."""
        start_time = time.time()
        try:
            # Validate user data
            user_data = {
                "username": username,
                "org_id": org_id,
                "roles": roles
            }
            validate_user_data(user_data)

            # Check if we're trying to create a user with elevated privileges
            if "admin" in roles or "super_admin" in roles:
                # Only super_admin can create other super_admin/admin users
                response = await self.client.get(f"/v1/orgs/{org_id}/users/me")
                if response.status_code == 404:
                    self.metrics.record_error("user_not_found")
                    raise ExchangeAPIError("Failed to get current user information")
                
                current_user = User(**response.json())
                validate_permission_level("super_admin", current_user.roles)

            response = await self.client.post(f"/v1/orgs/{org_id}/users", json={
                "username": username,
                "roles": roles
            })
            
            if response.status_code == 403:
                self.metrics.record_error("permission_error")
                raise PermissionError(
                    f"Insufficient permissions to create users in organization {org_id}",
                    required_permission="create_users"
                )
            
            result = User(**response.json())
            self._invalidate_cache(f"users:{org_id}")
            self.metrics.record_user_operation("create", True)
            self.metrics.record_response_time("create_user", time.time() - start_time)
            return result
        except (UserValidationError, PermissionError) as e:
            self.metrics.record_user_operation("create", False)
            self.metrics.record_error("validation_error" if isinstance(e, UserValidationError) else "permission_error")
            raise e
        except Exception as e:
            self.metrics.record_user_operation("create", False)
            self.metrics.record_error("api_error")
            raise ExchangeAPIError(f"Failed to create user {username}: {str(e)}")

    async def update_user(self, org_id: str, username: str, roles: List[str]) -> User:
        """Update user roles in an organization."""
        try:
            # Validate user data
            user_data = {
                "username": username,
                "org_id": org_id,
                "roles": roles
            }
            validate_user_data(user_data)

            data = {
                "roles": roles
            }
            response = await self.client.put(f"/v1/orgs/{org_id}/users/{username}", json=data)
            result = User(**response.json())
            self._invalidate_cache(f"users:{org_id}")
            self._invalidate_cache(f"user:{org_id}:{username}")
            return result
        except UserValidationError as e:
            raise e
        except Exception as e:
            raise ExchangeAPIError(f"Failed to update user {username}: {str(e)}")

    async def delete_user(self, org_id: str, username: str) -> None:
        """Delete a user from an organization."""
        try:
            await self.client.delete(f"/v1/orgs/{org_id}/users/{username}")
            self._invalidate_cache(f"users:{org_id}")
            self._invalidate_cache(f"user:{org_id}:{username}")
        except Exception as e:
            raise ExchangeAPIError(f"Failed to delete user {username}: {str(e)}")

    def save_metrics(self):
        """Save collected metrics to disk."""
        self.metrics.save_metrics()

    async def check_organization_health(self, org_id: str) -> Dict[str, Any]:
        """Check the health of an organization."""
        start_time = datetime.now()
        try:
            check = await self.health.check_organization_health(org_id, self.client)
            self.health.record_health_check(check)
            self.metrics.record_operation("health_check", "success", datetime.now() - start_time)
            return {
                "status": check.status,
                "message": check.message,
                "details": check.details,
                "timestamp": check.timestamp.isoformat()
            }
        except Exception as e:
            self.metrics.record_operation("health_check", "error", datetime.now() - start_time)
            self.metrics.record_error("health_check", str(e))
            raise
    
    async def check_user_health(self, org_id: str, username: str) -> Dict[str, Any]:
        """Check the health of a user."""
        start_time = datetime.now()
        try:
            check = await self.health.check_user_health(org_id, username, self.client)
            self.health.record_health_check(check)
            self.metrics.record_operation("user_health_check", "success", datetime.now() - start_time)
            return {
                "status": check.status,
                "message": check.message,
                "details": check.details,
                "timestamp": check.timestamp.isoformat()
            }
        except Exception as e:
            self.metrics.record_operation("user_health_check", "error", datetime.now() - start_time)
            self.metrics.record_error("user_health_check", str(e))
            raise
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of health check results."""
        return self.health.get_health_summary()
    
    def get_health_history(self) -> List[Dict[str, Any]]:
        """Get the history of health checks."""
        return [
            {
                "name": check.name,
                "status": check.status,
                "message": check.message,
                "timestamp": check.timestamp.isoformat(),
                "details": check.details
            }
            for check in self.health.get_health_history()
        ]
