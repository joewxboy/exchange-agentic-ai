from typing import Dict, List, Optional
from datetime import datetime
import re

class ValidationError(Exception):
    """Base class for validation errors."""
    pass

class OrganizationValidationError(ValidationError):
    """Raised when organization data validation fails."""
    pass

class UserValidationError(ValidationError):
    """Raised when user data validation fails."""
    pass

class PermissionValidationError(ValidationError):
    """Raised when permission validation fails."""
    pass

def validate_organization_name(name: str) -> bool:
    """Validate organization name format."""
    if not name or not isinstance(name, str):
        raise OrganizationValidationError("Organization name must be a non-empty string")
    
    # Name should be 3-50 characters, alphanumeric with hyphens and underscores
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-_]{2,49}$', name):
        raise OrganizationValidationError(
            "Organization name must be 3-50 characters, start with alphanumeric, "
            "and contain only alphanumeric characters, hyphens, and underscores"
        )
    return True

def validate_organization_description(description: Optional[str]) -> bool:
    """Validate organization description format."""
    if description is not None:
        if not isinstance(description, str):
            raise OrganizationValidationError("Description must be a string")
        if len(description) > 1000:
            raise OrganizationValidationError("Description must be 1000 characters or less")
    return True

def validate_username(username: str) -> bool:
    """Validate username format."""
    if not username or not isinstance(username, str):
        raise UserValidationError("Username must be a non-empty string")
    
    # Username should be 3-50 characters, alphanumeric with hyphens and underscores
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9-_]{2,49}$', username):
        raise UserValidationError(
            "Username must be 3-50 characters, start with alphanumeric, "
            "and contain only alphanumeric characters, hyphens, and underscores"
        )
    return True

def validate_roles(roles: List[str]) -> bool:
    """Validate user roles."""
    if not roles or not isinstance(roles, list):
        raise UserValidationError("Roles must be a non-empty list")
    
    valid_roles = {'user', 'admin', 'super_admin'}
    for role in roles:
        if not isinstance(role, str):
            raise UserValidationError("Each role must be a string")
        if role not in valid_roles:
            raise UserValidationError(f"Invalid role: {role}. Valid roles are: {', '.join(valid_roles)}")
    
    # Check for role hierarchy violations
    if 'super_admin' in roles and len(roles) > 1:
        raise UserValidationError("super_admin role cannot be combined with other roles")
    
    return True

def validate_organization_data(data: Dict) -> bool:
    """Validate complete organization data."""
    required_fields = {'name', 'org_id'}
    for field in required_fields:
        if field not in data:
            raise OrganizationValidationError(f"Missing required field: {field}")
    
    validate_organization_name(data['name'])
    validate_organization_description(data.get('description'))
    
    # Validate timestamps if present
    for field in ['created', 'last_updated']:
        if field in data:
            try:
                datetime.fromisoformat(data[field])
            except ValueError:
                raise OrganizationValidationError(f"Invalid {field} timestamp format")
    
    return True

def validate_user_data(data: Dict) -> bool:
    """Validate complete user data."""
    required_fields = {'username', 'org_id', 'roles'}
    for field in required_fields:
        if field not in data:
            raise UserValidationError(f"Missing required field: {field}")
    
    validate_username(data['username'])
    validate_roles(data['roles'])
    
    # Validate timestamps if present
    for field in ['created', 'last_updated']:
        if field in data:
            try:
                datetime.fromisoformat(data[field])
            except ValueError:
                raise UserValidationError(f"Invalid {field} timestamp format")
    
    return True

def validate_permission_level(required_level: str, user_roles: List[str]) -> bool:
    """Validate if user has required permission level."""
    from .organizations import PermissionLevel
    
    if not isinstance(required_level, str):
        raise PermissionValidationError("Required permission level must be a string")
    
    if not isinstance(user_roles, list):
        raise PermissionValidationError("User roles must be a list")
    
    user_level = PermissionLevel.from_roles(user_roles)
    required = PermissionLevel[required_level.upper()]
    
    if not user_level.can_perform(required):
        raise PermissionValidationError(
            f"Insufficient permissions. Required: {required_level}, User has: {user_level}"
        )
    
    return True 