"""
Service management module for Open Horizon Exchange API.
"""
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any

from src.exchange.client import ExchangeAPIClient

class ServiceListType(Enum):
    """Enumeration of service list types."""
    CATALOG = "catalog"
    USER = "user"
    PUBLIC = "public"
    ORG = "org"
    NODE = "node"

@dataclass
class ServiceInfo:
    """Data class for service information."""
    id: str
    name: str
    owner: str
    public: bool
    version: str
    arch: str
    description: str
    documentation: str
    deployment: Dict[str, Any]
    deployment_signature: str
    cluster_deployment: Optional[str] = None
    cluster_deployment_signature: Optional[str] = None
    state: Optional[str] = None

class ServiceManager:
    """Manager class for handling service-related operations."""
    
    def __init__(self, client: ExchangeAPIClient):
        """Initialize the service manager with an API client."""
        self.client = client
    
    async def get_service_list(self, list_type: ServiceListType) -> List[ServiceInfo]:
        """Get a list of services based on the specified type."""
        endpoint = f"/{list_type.value}/services"
        response = await self.client.get(endpoint)
        
        if not response or "services" not in response:
            return []
            
        services = []
        for service_id, service_data in response["services"].items():
            try:
                service = ServiceInfo(
                    id=service_id,
                    name=service_data.get("url", ""),
                    owner=service_data.get("owner", ""),
                    public=service_data.get("public", False),
                    version=service_data.get("version", ""),
                    arch=service_data.get("arch", ""),
                    description=service_data.get("description", ""),
                    documentation=service_data.get("documentation", ""),
                    deployment=service_data.get("deployment", {}),
                    deployment_signature=service_data.get("deploymentSignature", ""),
                    cluster_deployment=service_data.get("clusterDeployment"),
                    cluster_deployment_signature=service_data.get("clusterDeploymentSignature")
                )
                services.append(service)
            except Exception as e:
                print(f"Error parsing service {service_id}: {str(e)}")
                continue
                
        return services
    
    async def get_user_services(self, username: str) -> List[ServiceInfo]:
        """Get services published by a specific user."""
        return await self.get_service_list(ServiceListType.USER)
    
    async def get_public_services(self) -> List[ServiceInfo]:
        """Get public services."""
        return await self.get_service_list(ServiceListType.PUBLIC)
    
    async def get_org_services(self) -> List[ServiceInfo]:
        """Get services available to the organization."""
        return await self.get_service_list(ServiceListType.ORG)
    
    async def get_node_services(self, node_id: str) -> List[ServiceInfo]:
        """Get services running on a specific node."""
        return await self.get_service_list(ServiceListType.NODE) 