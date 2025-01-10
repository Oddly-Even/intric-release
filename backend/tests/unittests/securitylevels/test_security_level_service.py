# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from instorage.main.exceptions import BadRequestException, NotFoundException, UnauthorizedException
from instorage.roles.permissions import Permission
from instorage.securitylevels.security_level import SecurityLevel
from instorage.securitylevels.security_level_service import SecurityLevelService
from tests.fixtures import TEST_UUID

TEST_NAME = "test_security_level"
TEST_DESCRIPTION = "A test security level"
TEST_VALUE = 100


@pytest.fixture
def service():
    repo = AsyncMock()
    # Default to no existing security level with any name
    repo.get_by_name.return_value = None

    user = MagicMock()
    user.permissions = []  # Default to no permissions

    return SecurityLevelService(
        repo=repo,
        user=user,
    )


@pytest.fixture
def security_level():
    return SecurityLevel(
        id=TEST_UUID,
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        value=TEST_VALUE,
        created_at=None,
        updated_at=None,
    )


async def test_create_security_level(service, security_level):
    """Test creating a security level."""
    # Setup
    service.user.permissions = [Permission.ADMIN]
    service.repo.create.return_value = security_level

    # Execute
    result = await service.create_security_level(
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        value=TEST_VALUE,
    )

    # Assert
    assert result == security_level
    service.repo.create.assert_called_once()


async def test_create_security_level_no_permission(service):
    """Test creating a security level without admin permission."""
    # Setup - no permissions by default

    # Execute & Assert
    with pytest.raises(UnauthorizedException):
        await service.create_security_level(
            name=TEST_NAME,
            description=TEST_DESCRIPTION,
            value=TEST_VALUE,
        )

    service.repo.create.assert_not_called()


async def test_create_security_level_duplicate_name(service, security_level):
    """Test creating a security level with duplicate name."""
    # Setup
    service.user.permissions = [Permission.ADMIN]
    service.repo.get_by_name.return_value = security_level

    # Execute & Assert
    with pytest.raises(BadRequestException):
        await service.create_security_level(
            name=TEST_NAME,
            description=TEST_DESCRIPTION,
            value=TEST_VALUE,
        )

    service.repo.create.assert_not_called()


async def test_get_security_level(service, security_level):
    """Test getting a security level."""
    # Setup
    service.repo.get.return_value = security_level
    # No permissions needed for reading

    # Execute
    result = await service.get_security_level(TEST_UUID)

    # Assert
    assert result == security_level
    service.repo.get.assert_called_once_with(TEST_UUID)


async def test_get_security_level_not_found(service):
    """Test getting a non-existent security level."""
    # Setup
    service.repo.get.return_value = None
    # No permissions needed for reading

    # Execute & Assert
    with pytest.raises(NotFoundException):
        await service.get_security_level(TEST_UUID)


async def test_list_security_levels(service, security_level):
    """Test listing security levels."""
    # Setup
    service.repo.list_all.return_value = [security_level]
    # No permissions needed for reading

    # Execute
    result = await service.list_security_levels()

    # Assert
    assert result == [security_level]
    service.repo.list_all.assert_called_once()


async def test_update_security_level(service, security_level):
    """Test updating a security level."""
    # Setup
    service.user.permissions = [Permission.ADMIN]
    service.repo.get.return_value = security_level
    service.repo.update.return_value = security_level

    # Execute
    result = await service.update_security_level(
        id=TEST_UUID,
        name="updated_name",
        description="updated_description",
        value=200,
    )

    # Assert
    assert result == security_level
    service.repo.update.assert_called_once()


async def test_update_security_level_not_found(service):
    """Test updating a non-existent security level."""
    # Setup
    service.user.permissions = [Permission.ADMIN]
    service.repo.get.return_value = None

    # Execute & Assert
    with pytest.raises(NotFoundException):
        await service.update_security_level(
            id=TEST_UUID,
            name="updated_name",
        )

    service.repo.update.assert_not_called()


async def test_update_security_level_no_permission(service, security_level):
    """Test updating a security level without admin permission."""
    # Setup
    service.repo.get.return_value = security_level
    # No permissions by default

    # Execute & Assert
    with pytest.raises(UnauthorizedException):
        await service.update_security_level(
            id=TEST_UUID,
            name="updated_name",
        )

    service.repo.update.assert_not_called()


async def test_update_security_level_duplicate_name(service, security_level):
    """Test updating a security level with duplicate name."""
    # Setup
    service.user.permissions = [Permission.ADMIN]
    service.repo.get.return_value = security_level
    service.repo.get_by_name.return_value = SecurityLevel(
        id=uuid4(),
        name="existing_name",
        value=0,
    )

    # Execute & Assert
    with pytest.raises(BadRequestException):
        await service.update_security_level(
            id=TEST_UUID,
            name="existing_name",
        )

    service.repo.update.assert_not_called()


async def test_delete_security_level(service, security_level):
    """Test deleting a security level."""
    # Setup
    service.user.permissions = [Permission.ADMIN]
    service.repo.get.return_value = security_level

    # Execute
    await service.delete_security_level(TEST_UUID)

    # Assert
    service.repo.delete.assert_called_once_with(TEST_UUID)


async def test_delete_security_level_not_found(service):
    """Test deleting a non-existent security level."""
    # Setup
    service.user.permissions = [Permission.ADMIN]
    service.repo.get.return_value = None

    # Execute & Assert
    with pytest.raises(NotFoundException):
        await service.delete_security_level(TEST_UUID)

    service.repo.delete.assert_not_called()


async def test_delete_security_level_no_permission(service, security_level):
    """Test deleting a security level without admin permission."""
    # Setup
    service.repo.get.return_value = security_level
    # No permissions by default

    # Execute & Assert
    with pytest.raises(UnauthorizedException):
        await service.delete_security_level(TEST_UUID)

    service.repo.delete.assert_not_called()


async def test_get_security_level_by_name(service, security_level):
    """Test getting a security level by name."""
    # Setup
    service.repo.get_by_name.return_value = security_level
    # No permissions needed for reading

    # Execute
    result = await service.get_security_level_by_name(TEST_NAME)

    # Assert
    assert result == security_level
    service.repo.get_by_name.assert_called_once_with(TEST_NAME)


async def test_get_highest_security_level(service):
    """Test getting the highest security level value."""
    # Setup
    service.repo.get_highest_value.return_value = TEST_VALUE
    # No permissions needed for reading

    # Execute
    result = await service.get_highest_security_level()

    # Assert
    assert result == TEST_VALUE
    service.repo.get_highest_value.assert_called_once()
