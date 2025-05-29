from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

from src.exchange.client import ExchangeAPIClient

class ServiceListType(Enum):
    """Types of service lists that can be retrieved."""
    CATALOG = "catalog"           # All services in catalog
    USER_PUBLISHED = "user"       # User's published services
    PUBLIC = "public"            # All public services
    ORGANIZATION = "org"         # Org's available services
    NODE = "node"               # Services on specific node

@dataclass
class ServiceInfo:
    """Information about a service in the Open Horizon Exchange."""
    id: str
    name: str
    owner: str
    version: str
    arch: str
    public: bool
    state: str
    last_updated: datetime
    metadata: Dict[str, Any]
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> 'ServiceInfo':
        """Create a ServiceInfo instance from API response data."""
        return cls(
            id=data['id'],
            name=data['name'],
            owner=data['owner'],
            version=data['version'],
            arch=data['arch'],
            public=data.get('public', False),
            state=data.get('state', 'unknown'),
            last_updated=datetime.fromisoformat(data['lastUpdated']),
            metadata=data.get('metadata', {})
        )

class ServiceManager:
    """Manages service-related operations in the Open Horizon Exchange."""
    
    # Base endpoint structure
    SERVICE_ENDPOINTS = {
        ServiceListType.CATALOG: "/catalog/services",
        ServiceListType.USER_PUBLISHED: "/orgs/{org}/users/{username}/services",
        ServiceListType.PUBLIC: "/orgs/{org}/services?public=true",
        ServiceListType.ORGANIZATION: "/orgs/{org}/services?available=true",
        ServiceListType.NODE: "/orgs/{org}/nodes/{node}/services"
    }
    
    def __init__(self, client: ExchangeAPIClient):
        """Initialize the ServiceManager with an ExchangeAPIClient."""
        self.client = client
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    async def get_service_list(self, list_type: ServiceListType, **kwargs) -> List[ServiceInfo]:
        """Retrieve a list of services based on type and filters."""
        endpoint = self.SERVICE_ENDPOINTS[list_type].format(**kwargs)
        response = await self.client._make_request("GET", endpoint)
        return [ServiceInfo.from_api_response(service) for service in response]
    
    async def get_user_services(self, username: str) -> List[ServiceInfo]:
        """Get services published by a specific user."""
        return await self.get_service_list(
            ServiceListType.USER_PUBLISHED,
            org=self.client.org_id,
            username=username
        )
    
    async def get_public_services(self) -> List[ServiceInfo]:
        """Get all public services."""
        return await self.get_service_list(
            ServiceListType.PUBLIC,
            org=self.client.org_id
        )
    
    async def get_org_services(self) -> List[ServiceInfo]:
        """Get all services available to the organization."""
        return await self.get_service_list(
            ServiceListType.ORGANIZATION,
            org=self.client.org_id
        )
    
    async def get_node_services(self, node_id: str) -> List[ServiceInfo]:
        """Get all services running on a specific node."""
        return await self.get_service_list(
            ServiceListType.NODE,
            org=self.client.org_id,
            node=node_id
        )
    
    def filter_services(self, services: List[ServiceInfo], **filters) -> List[ServiceInfo]:
        """Filter services based on provided criteria."""
        filtered = services
        for key, value in filters.items():
            filtered = [s for s in filtered if getattr(s, key) == value]
        return filtered
    
    def sort_services(self, services: List[ServiceInfo], key: str, reverse: bool = False) -> List[ServiceInfo]:
        """Sort services based on the specified key."""
        return sorted(services, key=lambda x: getattr(x, key), reverse=reverse)
    
    async def get_service(self, service_id: str) -> Optional[ServiceInfo]:
        """Get detailed information about a specific service."""
        try:
            response = await self.client._make_request(
                "GET",
                f"/orgs/{self.client.org_id}/services/{service_id}"
            )
            return ServiceInfo.from_api_response(response)
        except Exception:
            return None
    
    async def search_services(self, query: str) -> List[ServiceInfo]:
        """Search for services matching the query string."""
        services = await self.get_org_services()
        return [
            service for service in services
            if query.lower() in service.name.lower() or
               query.lower() in service.id.lower() or
               query.lower() in service.owner.lower()
        ] 