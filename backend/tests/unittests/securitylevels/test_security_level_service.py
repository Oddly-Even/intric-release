# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4
from datetime import datetime

import pytest

from instorage.main.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from instorage.roles.permissions import Permission
from instorage.securitylevels.security_level import SecurityLevel, SecurityLevelCreate
from instorage.securitylevels.security_level_service import SecurityLevelService
from tests.fixtures import TEST_UUID, TEST_TENANT, TEST_USER
from instorage.users.user import UserInDB
from instorage.tenants.tenant import TenantInDB

TEST_NAME = "test_security_level"
TEST_DESCRIPTION = "A test security level"
TEST_VALUE = 100

TEST_TENANT_ID = UUID("6989cb80-a68b-4f4e-a75f-6336b13f36e0")
TEST_USER_ID = UUID("7989cb80-a68b-4f4e-a75f-6336b13f36e0")


@pytest.fixture
def mock_tenant():
    """Create a mock tenant for testing."""
    return TenantInDB(
        id=TEST_TENANT_ID,
        name="test_tenant",
        modules=[],
        quota_limit=1000000
    )


@pytest.fixture
def security_level():
    """Create a security level for testing."""
    return SecurityLevel(
        id=TEST_UUID,
        tenant_id=TEST_TENANT.id,
        name="test_level",
        description="Test security level",
        value=100,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )


@pytest.fixture
def service():
    """Create a service instance for testing."""
    repo = AsyncMock()
    return SecurityLevelService(user=TEST_USER, repo=repo)


@pytest.fixture
def service_no_permissions():
    """Create a service instance with no permissions for testing."""
    user = TEST_USER.model_copy(update={
        "roles": [],
        "predefined_roles": []
    })
    repo = AsyncMock()
    return SecurityLevelService(user=user, repo=repo)


@pytest.fixture
def higher_security_level():
    return SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="high_level",
        description="High security level",
        value=200,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )


async def test_create_security_level(service: SecurityLevelService):
    """Test creating a security level."""
    service.repo.get_by_name_and_tenant.return_value = None
    service.repo.create.return_value = MagicMock()

    await service.create_security_level(
        name="test_level",
        description="Test security level",
        value=100,
    )

    service.repo.get_by_name_and_tenant.assert_called_once_with(
        "test_level", service.user.tenant_id
    )
    service.repo.create.assert_called_once()


async def test_create_security_level_no_permission(service_no_permissions: SecurityLevelService):
    """Test creating a security level without permission."""
    with pytest.raises(UnauthorizedException):
        await service_no_permissions.create_security_level(
            name="test_level",
            description="Test security level",
            value=100,
        )


async def test_create_security_level_duplicate_name(service: SecurityLevelService):
    """Test creating a security level with a duplicate name."""
    service.repo.get_by_name_and_tenant.return_value = MagicMock()

    with pytest.raises(BadRequestException):
        await service.create_security_level(
            name="test_level",
            description="Test security level",
            value=100,
        )


async def test_get_security_level(service: SecurityLevelService, security_level: SecurityLevel):
    """Test getting a security level."""
    service.repo.get.return_value = security_level

    result = await service.get_security_level(TEST_UUID)

    assert result == security_level


async def test_get_security_level_not_found(service: SecurityLevelService):
    """Test getting a non-existent security level."""
    service.repo.get.return_value = None

    with pytest.raises(NotFoundException):
        await service.get_security_level(TEST_UUID)


async def test_get_security_level_wrong_tenant(service: SecurityLevelService):
    """Test getting a security level from wrong tenant."""
    wrong_tenant_level = SecurityLevel(
        id=TEST_UUID,
        tenant_id=uuid4(),  # Different tenant
        name="test_level",
        description="Test security level",
        value=100,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    service.repo.get.return_value = wrong_tenant_level

    with pytest.raises(NotFoundException):
        await service.get_security_level(TEST_UUID)


async def test_list_security_levels(service: SecurityLevelService):
    """Test listing security levels."""
    expected_levels = [MagicMock(), MagicMock()]
    service.repo.list_by_tenant.return_value = expected_levels

    result = await service.list_security_levels()

    assert result == expected_levels


async def test_update_security_level(service: SecurityLevelService, security_level: SecurityLevel):
    """Test updating a security level."""
    service.repo.get.return_value = security_level
    service.repo.get_by_name_and_tenant.return_value = None
    service.repo.update.return_value = MagicMock()

    await service.update_security_level(
        id=TEST_UUID,
        name="new_name",
        description="New description",
        value=200,
    )

    service.repo.update.assert_called_once()


async def test_update_security_level_not_found(service: SecurityLevelService):
    """Test updating a non-existent security level."""
    service.repo.get.return_value = None

    with pytest.raises(NotFoundException):
        await service.update_security_level(
            id=TEST_UUID,
            name="new_name",
            description="New description",
            value=200,
        )


async def test_update_security_level_wrong_tenant(service: SecurityLevelService):
    """Test updating a security level from wrong tenant."""
    wrong_tenant_level = SecurityLevel(
        id=TEST_UUID,
        tenant_id=uuid4(),  # Different tenant
        name="test_level",
        description="Test security level",
        value=100,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    service.repo.get.return_value = wrong_tenant_level

    with pytest.raises(NotFoundException):
        await service.update_security_level(
            id=TEST_UUID,
            name="new_name",
            description="New description",
            value=200,
        )


async def test_update_security_level_no_permission(service_no_permissions: SecurityLevelService):
    """Test updating a security level without permission."""
    with pytest.raises(UnauthorizedException):
        await service_no_permissions.update_security_level(
            id=TEST_UUID,
            name="new_name",
            description="New description",
            value=200,
        )


async def test_update_security_level_duplicate_name(service: SecurityLevelService, security_level: SecurityLevel):
    """Test updating a security level with a duplicate name."""
    service.repo.get.return_value = security_level
    existing_level = SecurityLevel(
        id=uuid4(),  # Different ID
        tenant_id=TEST_TENANT.id,
        name="new_name",
        description="Existing level",
        value=100,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    service.repo.get_by_name_and_tenant.return_value = existing_level

    with pytest.raises(BadRequestException):
        await service.update_security_level(
            id=TEST_UUID,
            name="new_name",
        )


async def test_delete_security_level(service: SecurityLevelService, security_level: SecurityLevel):
    """Test deleting a security level."""
    service.repo.get.return_value = security_level

    await service.delete_security_level(TEST_UUID)

    service.repo.delete.assert_called_once_with(TEST_UUID)


async def test_delete_security_level_not_found(service: SecurityLevelService):
    """Test deleting a non-existent security level."""
    service.repo.get.return_value = None

    with pytest.raises(NotFoundException):
        await service.delete_security_level(TEST_UUID)


async def test_delete_security_level_wrong_tenant(service: SecurityLevelService):
    """Test deleting a security level from wrong tenant."""
    wrong_tenant_level = SecurityLevel(
        id=TEST_UUID,
        tenant_id=uuid4(),  # Different tenant
        name="test_level",
        description="Test security level",
        value=100,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )
    service.repo.get.return_value = wrong_tenant_level

    with pytest.raises(NotFoundException):
        await service.delete_security_level(TEST_UUID)


async def test_delete_security_level_no_permission(service_no_permissions: SecurityLevelService):
    """Test deleting a security level without permission."""
    with pytest.raises(UnauthorizedException):
        await service_no_permissions.delete_security_level(TEST_UUID)