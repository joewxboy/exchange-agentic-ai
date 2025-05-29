import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.organizations import OrganizationManager, OrganizationInfo, User, PermissionError, PermissionLevel
from src.exchange_client import ExchangeAPIClient

class MockResponse:
    def __init__(self, json_data, status_code=200):
        self._json_data = json_data
        self.status_code = status_code
    def json(self):
        return self._json_data

@pytest.fixture
def mock_client():
    client = MagicMock(spec=ExchangeAPIClient)
    client.org_id = "test-org"
    client.get = AsyncMock()
    client.post = AsyncMock()
    client.delete = AsyncMock()
    return client

@pytest.fixture
def org_manager(mock_client):
    return OrganizationManager(mock_client)

@pytest.fixture
def sample_org_data():
    return {
        "org_id": "test-org",
        "name": "TestOrg",
        "description": "Test organization description",
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

@pytest.fixture
def sample_user_data():
    return {
        "username": "test-user",
        "org_id": "test-org",
        "roles": ["user"],
        "created": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }

@pytest.mark.asyncio
async def test_get_organizations(org_manager, mock_client, sample_org_data):
    mock_client.get.return_value = MockResponse([sample_org_data])
    orgs = await org_manager.get_organizations()
    assert len(orgs) == 1
    assert orgs[0].org_id == sample_org_data["org_id"]
    mock_client.get.assert_called_once_with("/v1/orgs")

@pytest.mark.asyncio
async def test_get_organization(org_manager, mock_client, sample_org_data):
    mock_client.get.return_value = MockResponse(sample_org_data)
    org = await org_manager.get_organization("test-org")
    assert org.org_id == sample_org_data["org_id"]
    mock_client.get.assert_called_once_with("/v1/orgs/test-org")

@pytest.mark.asyncio
async def test_create_organization(org_manager, mock_client, sample_org_data):
    mock_client.post.return_value = MockResponse(sample_org_data)
    org = await org_manager.create_organization("TestOrg", "Test organization description")
    assert org.org_id == sample_org_data["org_id"]
    mock_client.post.assert_called_once_with("/v1/orgs", json={"name": "TestOrg", "description": "Test organization description"})

@pytest.mark.asyncio
async def test_create_organization_permission_error(org_manager, mock_client):
    mock_client.post.return_value = MockResponse({}, status_code=403)
    with pytest.raises(PermissionError):
        await org_manager.create_organization("NewOrg", "Test description")

@pytest.mark.asyncio
async def test_create_user(org_manager, mock_client, sample_user_data):
    mock_client.post.return_value = MockResponse(sample_user_data)
    user = await org_manager.create_user("test-org", "test-user", ["user"])
    assert user.username == sample_user_data["username"]
    mock_client.post.assert_called_once_with("/v1/orgs/test-org/users", json={"username": "test-user", "roles": ["user"]})

@pytest.mark.asyncio
async def test_create_user_with_elevated_permissions(org_manager, mock_client, sample_user_data):
    # Provide all required fields for the current user
    now = datetime.now().isoformat()
    mock_current_user = {
        "username": "admin_user",
        "org_id": "test-org",
        "roles": ["super_admin"],
        "created": now,
        "last_updated": now
    }
    mock_client.get.return_value = MockResponse(mock_current_user)
    mock_client.post.return_value = MockResponse({"username": "new_admin", "org_id": "test-org", "roles": ["admin"], "created": now, "last_updated": now})
    user = await org_manager.create_user("test-org", "new_admin", ["admin"])
    assert user.username == "new_admin"
    assert mock_client.get.call_count == 1
    assert mock_client.post.call_count == 1

@pytest.mark.asyncio
async def test_create_user_permission_error(org_manager, mock_client):
    mock_client.post.return_value = MockResponse({}, status_code=403)
    with pytest.raises(PermissionError):
        await org_manager.create_user("test-org", "test-user", ["user"])

@pytest.mark.asyncio
async def test_delete_organization(org_manager, mock_client):
    mock_client.delete.return_value = MockResponse({"status": "deleted"})
    await org_manager.delete_organization("test-org")
    mock_client.delete.assert_called_once_with("/v1/orgs/test-org")

@pytest.mark.asyncio
async def test_delete_organization_permission_error(org_manager, mock_client):
    mock_client.delete.return_value = MockResponse({}, status_code=403)
    with pytest.raises(Exception):
        await org_manager.delete_organization("test-org")

@pytest.mark.asyncio
async def test_permission_level():
    assert PermissionLevel.from_roles(["user"]) == PermissionLevel.USER
    assert PermissionLevel.from_roles(["admin"]) == PermissionLevel.ADMIN
    assert PermissionLevel.from_roles(["super_admin"]) == PermissionLevel.SUPER_ADMIN
    assert PermissionLevel.from_roles(["user", "admin"]) == PermissionLevel.ADMIN
    assert PermissionLevel.from_roles(["user", "admin", "super_admin"]) == PermissionLevel.SUPER_ADMIN

@pytest.mark.asyncio
async def test_permission_level_can_perform():
    user_level = PermissionLevel.USER
    admin_level = PermissionLevel.ADMIN
    super_admin_level = PermissionLevel.SUPER_ADMIN

    assert user_level.can_perform(PermissionLevel.USER)
    assert admin_level.can_perform(PermissionLevel.USER)
    assert super_admin_level.can_perform(PermissionLevel.USER)

    assert not user_level.can_perform(PermissionLevel.ADMIN)
    assert admin_level.can_perform(PermissionLevel.ADMIN)
    assert super_admin_level.can_perform(PermissionLevel.ADMIN)

    assert not user_level.can_perform(PermissionLevel.SUPER_ADMIN)
    assert not admin_level.can_perform(PermissionLevel.SUPER_ADMIN)
    assert super_admin_level.can_perform(PermissionLevel.SUPER_ADMIN) 