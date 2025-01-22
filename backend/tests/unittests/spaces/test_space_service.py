from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from instorage.main.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
)
from instorage.spaces.api.space_models import SpaceRole
from instorage.spaces.space_service import SpaceService
from tests.fixtures import TEST_USER, TEST_UUID, TEST_TENANT
from instorage.securitylevels.security_level import SecurityLevel


@pytest.fixture
async def service():
    service = SpaceService(
        repo=AsyncMock(),
        factory=MagicMock(),
        user_repo=AsyncMock(),
        ai_models_service=AsyncMock(),
        security_level_service=AsyncMock(),
        user=TEST_USER,
    )

    return service


async def test_create_space_is_created_with_all_available_completion_models(
    service: SpaceService,
):
    space = MagicMock()
    available_model = MagicMock(can_access=True)
    not_available_model = MagicMock(can_access=False)
    completion_models = [available_model, not_available_model]
    service.factory.create_space.return_value = space
    service.ai_models_service.get_completion_models.return_value = completion_models

    await service.create_space(MagicMock())

    assert space.completion_models == [available_model]


async def test_create_space_is_created_with_latest_available_embedding_model(
    service: SpaceService,
):
    space = MagicMock()
    embedding_models = [
        MagicMock(created_at=datetime(2024, 1, 3 - i), can_access=True)
        for i in range(3)
    ]
    service.factory.create_space.return_value = space
    service.ai_models_service.get_embedding_models.return_value = embedding_models

    await service.create_space(MagicMock())

    assert space.embedding_models == [embedding_models[0]]


async def test_raise_not_found_if_not_found(service: SpaceService):
    service.repo.get.return_value = None

    with pytest.raises(NotFoundException):
        await service.get_space(uuid4())


async def test_raise_not_found_if_user_not_member_of_space(service: SpaceService):
    space = MagicMock()
    space.can_read.return_value = False
    service.repo.get.return_value = space

    with pytest.raises(NotFoundException):
        await service.get_space(uuid4())


async def test_raise_unauthorized_if_user_can_not_edit(service: SpaceService):
    space = MagicMock()
    space.can_edit.return_value = False
    service.repo.get.return_value = space

    with pytest.raises(UnauthorizedException):
        await service.update_space(uuid4(), MagicMock())


async def test_raise_unauthorized_if_user_can_not_delete(service: SpaceService):
    space = MagicMock()
    space.can_edit.return_value = False
    service.repo.get.return_value = space

    with pytest.raises(UnauthorizedException):
        await service.delete_space(uuid4())


async def test_user_can_not_delete_personal_space(service: SpaceService):
    space = MagicMock()
    space.user_id = uuid4()
    service.repo.get.return_value = space

    with pytest.raises(UnauthorizedException):
        await service.delete_space(uuid4())


async def test_only_admins_can_add_members(service: SpaceService):
    space = MagicMock()
    space.can_edit.return_value = False
    service.repo.get.return_value = space
    service.user_repo.get_user_by_id_and_tenant_id.return_value = MagicMock(
        email="test@test.com", username="username"
    )

    with pytest.raises(UnauthorizedException):
        await service.add_member(MagicMock(), MagicMock(), role=SpaceRole.EDITOR)


async def test_only_admins_can_delete_members(service: SpaceService):
    space = MagicMock()
    space.can_edit.return_value = False
    service.repo.get.return_value = space

    with pytest.raises(UnauthorizedException):
        await service.remove_member(MagicMock(), MagicMock())


async def test_can_not_remove_self(service: SpaceService):
    id = uuid4()
    service.user = MagicMock(id=id)

    with pytest.raises(BadRequestException):
        await service.remove_member(MagicMock(), id)


async def test_only_admins_can_change_role_of_member(service: SpaceService):
    space = MagicMock()
    space.can_edit.return_value = False
    service.repo.get.return_value = space

    with pytest.raises(UnauthorizedException):
        await service.change_role_of_member(MagicMock(), MagicMock(), MagicMock())


async def test_can_not_change_role_of_self(service: SpaceService):
    id = uuid4()
    service.user = MagicMock(id=id)

    with pytest.raises(BadRequestException):
        await service.change_role_of_member(MagicMock(), id, MagicMock())


async def test_get_personal_space_returns_all_available_completion_models(
    service: SpaceService,
):
    personal_space = MagicMock()
    completion_models = [MagicMock(), MagicMock()]
    service.repo.get_personal_space.return_value = personal_space
    service.ai_models_service.get_completion_models.return_value = completion_models

    space = await service.get_personal_space()

    assert space.completion_models == completion_models


async def test_get_personal_space_returns_all_available_embedding_models(
    service: SpaceService,
):
    personal_space = MagicMock()
    embedding_models = [MagicMock(), MagicMock()]
    service.repo.get_personal_space.return_value = personal_space
    service.ai_models_service.get_embedding_models.return_value = embedding_models

    space = await service.get_personal_space()

    assert space.embedding_models == embedding_models


async def test_get_spaces_and_personal_space_returns_personal_space_first(
    service: SpaceService,
):
    personal_space = MagicMock()
    other_spaces = [MagicMock(), MagicMock(), MagicMock()]

    service.repo.get_personal_space.return_value = personal_space
    service.repo.get_spaces.return_value = other_spaces

    spaces = await service.get_spaces(include_personal=True)

    assert spaces == [personal_space] + other_spaces


@pytest.fixture
def security_level():
    return SecurityLevel(
        id=TEST_UUID,
        tenant_id=TEST_TENANT.id,
        name="test_level",
        description="Test security level",
        value=100,
        created_at="2024-01-01T00:00:00",
        updated_at="2024-01-01T00:00:00",
    )


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


async def test_update_space_security_level(
    service: SpaceService, security_level: SecurityLevel
):
    """Test updating a space's security level."""
    space = MagicMock()
    space.can_edit.return_value = True

    service.get_space = AsyncMock(return_value=space)
    service.security_level_service.get_security_level = AsyncMock(return_value=security_level)

    await service.update_space(
        id=TEST_UUID,
        security_level_id=security_level.id,
    )

    # Check that update was called with the security level
    space.update.assert_called_once_with(
        name=None,
        description=None,
        completion_models=None,
        embedding_models=None,
        security_level=security_level,
    )
