#!/usr/bin/env python3

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceDefinition:
    """Class for storing service definition data."""
    owner: str
    label: str
    description: str
    public: bool
    documentation: str
    url: str
    version: str
    arch: str
    sharable: str
    matchHardware: Dict
    requiredServices: List[Dict]
    userInput: List[Dict]
    deployment: Dict
    deploymentSignature: str
    clusterDeployment: str
    clusterDeploymentSignature: str
    imageStore: Dict
    lastUpdated: Optional[datetime] = None

class ServiceManager:
    """Manages service-related operations and validation."""
    
    def __init__(self, client):
        """Initialize the service manager with an API client."""
        self.client = client
    
    def validate_service_data(self, service_data: Dict) -> bool:
        """Validate service data before creation or update."""
        required_fields = [
            'owner', 'label', 'description', 'public', 'documentation',
            'url', 'version', 'arch', 'sharable', 'matchHardware',
            'requiredServices', 'userInput', 'deployment'
        ]
        
        # Check for required fields
        for field in required_fields:
            if field not in service_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate version format (semantic versioning)
        version = service_data['version']
        if not self._is_valid_version(version):
            raise ValueError(f"Invalid version format: {version}")
        
        # Validate architecture
        arch = service_data['arch']
        if not self._is_valid_architecture(arch):
            raise ValueError(f"Invalid architecture: {arch}")
        
        # Validate sharable value
        sharable = service_data['sharable']
        if sharable not in ['singleton', 'multiple']:
            raise ValueError(f"Invalid sharable value: {sharable}")
        
        # Validate deployment format
        deployment = service_data['deployment']
        if not self._is_valid_deployment(deployment):
            raise ValueError("Invalid deployment format")
        
        return True
    
    def _is_valid_version(self, version: str) -> bool:
        """Check if version string follows semantic versioning."""
        try:
            parts = version.split('.')
            if len(parts) != 3:
                return False
            for part in parts:
                if not part.isdigit():
                    return False
            return True
        except Exception:
            return False
    
    def _is_valid_architecture(self, arch: str) -> bool:
        """Check if architecture is valid."""
        valid_archs = ['amd64', 'arm64', 'arm', 'ppc64le', 's390x']
        return arch in valid_archs
    
    def _is_valid_deployment(self, deployment: Dict) -> bool:
        """Validate deployment configuration."""
        if not isinstance(deployment, dict):
            return False
        
        # Check for required deployment fields
        if 'services' not in deployment:
            return False
        
        services = deployment['services']
        if not isinstance(services, dict):
            return False
        
        # Validate each service configuration
        for service_name, service_config in services.items():
            if not isinstance(service_config, dict):
                return False
            if 'image' not in service_config:
                return False
        
        return True
    
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