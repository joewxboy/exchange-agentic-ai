#!/usr/bin/env python3

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class ServiceDefinition(BaseModel):
    """Model for service definition data."""
    owner: str
    label: str
    description: str
    public: bool
    documentation: str
    url: str
    version: str
    arch: str
    sharable: str
    matchHardware: Dict = Field(default_factory=dict)
    requiredServices: List[Dict] = Field(default_factory=list)
    userInput: List[Dict] = Field(default_factory=list)
    deployment: Dict
    deploymentSignature: str
    clusterDeployment: Optional[str] = None
    clusterDeploymentSignature: Optional[str] = None
    imageStore: Optional[Dict] = Field(default_factory=dict)
    lastUpdated: Optional[datetime] = None

    @validator('version')
    def validate_version(cls, v):
        """Validate version format (semantic versioning)."""
        import re
        if not re.match(r'^\d+\.\d+\.\d+$', v):
            raise ValueError(f"Invalid version format: {v}")
        return v

    @validator('arch')
    def validate_architecture(cls, v):
        """Validate architecture."""
        valid_archs = {'amd64', 'arm64', 'arm', 'ppc64le', 's390x'}
        if v not in valid_archs:
            raise ValueError(f"Invalid architecture: {v}")
        return v

    @validator('sharable')
    def validate_sharable(cls, v):
        """Validate sharable value."""
        if v not in {'singleton', 'multiple'}:
            raise ValueError(f"Invalid sharable value: {v}")
        return v

    @validator('deployment')
    def validate_deployment(cls, v):
        """Validate deployment format."""
        if not isinstance(v, dict) or 'services' not in v:
            raise ValueError("Invalid deployment format: must contain 'services' key")
        return v

    @classmethod
    def from_api_response(cls, data: Dict) -> 'ServiceDefinition':
        """Create a ServiceDefinition instance from API response data."""
        return cls(**data)

class ServiceManager:
    """Manages service-related operations and validation."""
    
    def __init__(self, client):
        """Initialize the service manager with an API client."""
        self.client = client
    
    def validate_service_data(self, service_data: Dict) -> bool:
        """Validate service data before creation or update."""
        try:
            ServiceDefinition(**service_data)
            return True
        except Exception as e:
            raise ValueError(f"Service validation failed: {str(e)}")
    
    def create_service(self, org_id: str, service_data: Dict) -> Dict:
        """Create a new service with validation."""
        self.validate_service_data(service_data)
        return self.client.create_service(org_id, service_data)
    
    def update_service(self, org_id: str, service: str, service_data: Dict) -> Dict:
        """Update an existing service with validation."""
        self.validate_service_data(service_data)
        return self.client.update_service(org_id, service, service_data)
    
    def delete_service(self, org_id: str, service: str) -> Dict:
        """Delete a service with dependency checks."""
        # TODO: Implement dependency checking
        return self.client.delete_service(org_id, service)
    
    def search_services(self, org_id: str, query: str) -> List[Dict]:
        """Search for services matching the query."""
        services = self.client.list_services(org_id)
        if not query:
            return services
        
        query = query.lower()
        return [
            service for service in services
            if query in service.get('label', '').lower() or
               query in service.get('description', '').lower() or
               query in service.get('url', '').lower()
        ]
    
    def get_service_versions(self, org_id: str, service: str) -> List[str]:
        """Get all versions of a service."""
        services = self.client.list_services(org_id)
        versions = []
        
        for svc in services:
            if svc.get('url') == service:
                versions.append(svc.get('version'))
        
        return sorted(versions, key=lambda v: [int(x) for x in v.split('.')]) 