import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from openhorizon_client.service import ServiceInfo, ServiceManager, ServiceListType
from openhorizon_client.client import ExchangeAPIClient

@pytest.fixture
def mock_client():
    client = MagicMock(spec=ExchangeAPIClient)
    client.org_id = "test-org"
    client._make_request = AsyncMock()
    return client

@pytest.fixture
def service_manager(mock_client):
    return ServiceManager(mock_client)

@pytest.fixture
def sample_service_data():
    return {
        "id": "test-service",
        "name": "Test Service",
        "owner": "test-user",
        "version": "1.0.0",
        "arch": "amd64",
        "public": True,
        "state": "active",
        "lastUpdated": "2024-03-20T12:00:00Z",
        "metadata": {"description": "Test service"}
    }

@pytest.fixture
def sample_service(sample_service_data):
    return ServiceInfo.from_api_response(sample_service_data)

async def test_get_service_list(service_manager, mock_client, sample_service_data):
    mock_client._make_request.return_value = [sample_service_data]
    
    services = await service_manager.get_service_list(ServiceListType.CATALOG)
    
    assert len(services) == 1
    assert services[0].id == sample_service_data["id"]
    assert services[0].name == sample_service_data["name"]
    mock_client._make_request.assert_called_once_with(
        "GET",
        "/catalog/services"
    )

async def test_get_user_services(service_manager, mock_client, sample_service_data):
    mock_client._make_request.return_value = [sample_service_data]
    
    services = await service_manager.get_user_services("test-user")
    
    assert len(services) == 1
    assert services[0].owner == "test-user"
    mock_client._make_request.assert_called_once_with(
        "GET",
        "/orgs/test-org/users/test-user/services"
    )

async def test_get_public_services(service_manager, mock_client, sample_service_data):
    mock_client._make_request.return_value = [sample_service_data]
    
    services = await service_manager.get_public_services()
    
    assert len(services) == 1
    assert services[0].public is True
    mock_client._make_request.assert_called_once_with(
        "GET",
        "/orgs/test-org/services?public=true"
    )

async def test_get_org_services(service_manager, mock_client, sample_service_data):
    mock_client._make_request.return_value = [sample_service_data]
    
    services = await service_manager.get_org_services()
    
    assert len(services) == 1
    mock_client._make_request.assert_called_once_with(
        "GET",
        "/orgs/test-org/services?available=true"
    )

async def test_get_node_services(service_manager, mock_client, sample_service_data):
    mock_client._make_request.return_value = [sample_service_data]
    
    services = await service_manager.get_node_services("test-node")
    
    assert len(services) == 1
    mock_client._make_request.assert_called_once_with(
        "GET",
        "/orgs/test-org/nodes/test-node/services"
    )

def test_filter_services(service_manager, sample_service):
    services = [sample_service]
    
    filtered = service_manager.filter_services(services, public=True)
    assert len(filtered) == 1
    
    filtered = service_manager.filter_services(services, public=False)
    assert len(filtered) == 0

def test_sort_services(service_manager, sample_service):
    services = [
        ServiceInfo(
            id="service1",
            name="Service A",
            owner="user1",
            version="1.0.0",
            arch="amd64",
            public=True,
            state="active",
            last_updated=datetime.now(),
            metadata={}
        ),
        ServiceInfo(
            id="service2",
            name="Service B",
            owner="user2",
            version="1.0.0",
            arch="amd64",
            public=True,
            state="active",
            last_updated=datetime.now(),
            metadata={}
        )
    ]
    
    sorted_services = service_manager.sort_services(services, "name")
    assert sorted_services[0].name == "Service A"
    assert sorted_services[1].name == "Service B"
    
    sorted_services = service_manager.sort_services(services, "name", reverse=True)
    assert sorted_services[0].name == "Service B"
    assert sorted_services[1].name == "Service A"

async def test_get_service(service_manager, mock_client, sample_service_data):
    mock_client._make_request.return_value = sample_service_data
    
    service = await service_manager.get_service("test-service")
    
    assert service is not None
    assert service.id == "test-service"
    mock_client._make_request.assert_called_once_with(
        "GET",
        "/orgs/test-org/services/test-service"
    )

async def test_get_service_not_found(service_manager, mock_client):
    mock_client._make_request.side_effect = Exception("Service not found")
    
    service = await service_manager.get_service("non-existent")
    
    assert service is None

async def test_search_services(service_manager, mock_client, sample_service_data):
    mock_client._make_request.return_value = [sample_service_data]
    
    services = await service_manager.search_services("test")
    
    assert len(services) == 1
    assert services[0].id == "test-service"
    
    services = await service_manager.search_services("nonexistent")
    assert len(services) == 0 