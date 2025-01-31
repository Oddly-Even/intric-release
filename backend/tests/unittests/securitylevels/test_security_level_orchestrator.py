# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from datetime import datetime

from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from instorage.ai_models.completion_models.completion_model import (
    CompletionModelFamily,
    CompletionModelSparse,
    ModelHostingLocation,
    ModelStability,
)
from instorage.ai_models.embedding_models.embedding_model import (
    EmbeddingModelFamily,
    EmbeddingModelSparse,
)
from instorage.main.exceptions import BadRequestException, NotFoundException
from instorage.securitylevels.api.security_level_models import SecurityLevelSparse
from instorage.securitylevels.security_level import SecurityLevel
from instorage.securitylevels.security_level_orchestrator import (
    SecurityLevelOrchestrator,
    SecurityLevelResponse,
    SpaceSecurityAnalysisResponse,
    SecurityLevelChangeAnalysis,
)
from instorage.spaces.api.space_models import SpaceUpdateDryRunResponse
from tests.fixtures import TEST_UUID, TEST_TENANT, TEST_USER
from instorage.tenants.tenant import TenantInDB

TEST_NAME = "test_security_level"
TEST_DESCRIPTION = "A test security level"
TEST_VALUE = 100


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
def mock_service():
    """Create a mock security level service."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_model_access():
    """Create a mock model access implementation."""
    model_access = AsyncMock()

    # Mock model retrieval methods
    async def get_completion_model(id: UUID, include_non_accessible: bool = False):
        return MagicMock(id=id, security_level=None)

    async def get_embedding_model(id: UUID, include_non_accessible: bool = False):
        return MagicMock(id=id, security_level=None)

    model_access.get_completion_model = get_completion_model
    model_access.get_embedding_model = get_embedding_model
    return model_access


@pytest.fixture
def mock_space_repo():
    """Create a mock space repository."""
    repo = AsyncMock()

    # Default to no spaces affected
    repo.get_spaces_by_security_level.return_value = []
    return repo


@pytest.fixture
def mock_space_repo_with_spaces():
    """Create a mock space repository with affected spaces."""
    repo = AsyncMock()

    # Mock space retrieval methods with affected spaces
    affected_space = MagicMock(
        id=uuid4(),
        completion_models=[MagicMock(id=uuid4())],
        embedding_models=[MagicMock(id=uuid4())],
    )
    repo.get_spaces_by_security_level.return_value = [affected_space]
    return repo


@pytest.fixture
def orchestrator(mock_service, mock_model_access, mock_space_repo):
    """Create an orchestrator instance for testing."""
    return SecurityLevelOrchestrator(
        user=TEST_USER,
        security_level_service=mock_service,
        model_access=mock_model_access,
        space_repo=mock_space_repo,
    )


@pytest.fixture
def orchestrator_with_spaces(
    mock_service, mock_model_access, mock_space_repo_with_spaces
):
    """Create an orchestrator instance with affected spaces for testing."""
    return SecurityLevelOrchestrator(
        user=TEST_USER,
        security_level_service=mock_service,
        model_access=mock_model_access,
        space_repo=mock_space_repo_with_spaces,
    )


async def test_create_security_level(
    orchestrator: SecurityLevelOrchestrator, security_level: SecurityLevel
):
    """Test creating a security level with impact analysis."""
    # Setup
    orchestrator.security_level_service.create_security_level.return_value = (
        security_level
    )

    # Execute
    result = await orchestrator.create_security_level(
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        value=TEST_VALUE,
    )

    # Verify
    assert isinstance(result, SecurityLevelResponse)
    assert result.security_level == security_level
    assert result.warning is None
    orchestrator.security_level_service.create_security_level.assert_called_once_with(
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        value=TEST_VALUE,
    )


async def test_create_security_level_with_impact(
    orchestrator_with_spaces: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test creating a security level that affects existing spaces."""
    # Setup
    orchestrator_with_spaces.security_level_service.create_security_level.return_value = security_level

    # Execute
    result = await orchestrator_with_spaces.create_security_level(
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        value=TEST_VALUE,
    )

    # Verify
    assert isinstance(result, SecurityLevelResponse)
    assert result.security_level == security_level
    assert result.warning is not None
    assert "affect" in result.warning
    assert "1 spaces" in result.warning


async def test_update_security_level(
    orchestrator: SecurityLevelOrchestrator, security_level: SecurityLevel
):
    """Test updating a security level."""
    # Setup
    orchestrator.security_level_service.get_security_level.return_value = security_level
    orchestrator.security_level_service.update_security_level.return_value = (
        security_level
    )

    # Execute
    result = await orchestrator.update_security_level(
        id=TEST_UUID,
        name="new_name",
        description="New description",
        value=200,
    )

    # Verify
    assert isinstance(result, SecurityLevelResponse)
    assert result.security_level == security_level
    assert result.warning is None
    orchestrator.security_level_service.update_security_level.assert_called_once_with(
        id=TEST_UUID,
        name="new_name",
        description="New description",
        value=200,
    )


async def test_update_security_level_with_impact(
    orchestrator_with_spaces: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test updating a security level that affects existing spaces."""
    # Setup
    orchestrator_with_spaces.security_level_service.get_security_level.return_value = (
        security_level
    )
    orchestrator_with_spaces.security_level_service.update_security_level.return_value = security_level

    # Execute
    result = await orchestrator_with_spaces.update_security_level(
        id=TEST_UUID,
        value=200,  # Only changing value to trigger analysis
    )

    # Verify
    assert isinstance(result, SecurityLevelResponse)
    assert result.security_level == security_level
    assert result.warning is not None
    assert "affect" in result.warning
    assert "1 spaces" in result.warning


async def test_delete_security_level(
    orchestrator: SecurityLevelOrchestrator, security_level: SecurityLevel
):
    """Test deleting a security level."""
    # Setup
    orchestrator.security_level_service.get_security_level.return_value = security_level

    # Execute
    await orchestrator.delete_security_level(TEST_UUID)

    # Verify
    orchestrator.security_level_service.delete_security_level.assert_called_once_with(
        TEST_UUID
    )


async def test_delete_security_level_in_use(
    orchestrator_with_spaces: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test deleting a security level that is in use."""
    # Setup
    orchestrator_with_spaces.security_level_service.get_security_level.return_value = (
        security_level
    )

    # Execute and verify
    with pytest.raises(BadRequestException) as exc:
        await orchestrator_with_spaces.delete_security_level(TEST_UUID)

    assert "Cannot delete security level" in str(exc.value)
    assert "1 spaces" in str(exc.value)
    orchestrator_with_spaces.security_level_service.delete_security_level.assert_not_called()


async def test_analyze_security_level_update(
    orchestrator_with_spaces: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test analyzing security level updates."""
    # Setup
    orchestrator_with_spaces.security_level_service.get_security_level.return_value = (
        security_level
    )

    # Execute
    analysis = await orchestrator_with_spaces.analyze_security_level_update(
        id=TEST_UUID,
        value=200,  # Higher security level
    )

    # Verify
    assert isinstance(analysis, SecurityLevelChangeAnalysis)
    assert len(analysis.affected_spaces) > 0
    assert analysis.current_security_level == security_level
    assert analysis.new_security_level.value == 200


async def test_analyze_space_security_level_change(
    orchestrator: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test analyzing space security level changes with no impact."""
    # Setup
    space_id = uuid4()
    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=50,  # Lower security level
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Execute
    result = await orchestrator.analyze_space_security_level_change(
        space_id=space_id,
        current_security_level=security_level,
        new_security_level=new_security_level,
    )

    # Verify
    assert isinstance(result, SpaceSecurityAnalysisResponse)
    assert result.affected_space is None
    assert result.warning is None


async def test_analyze_space_security_level_change_with_impact(
    orchestrator_with_spaces: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test analyzing a space's security level change that affects models."""
    # Setup
    space_id = uuid4()
    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=200,  # Higher security level
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Mock affected models
    completion_model_id = uuid4()
    embedding_model_id = uuid4()
    safe_completion_model_id = uuid4()
    safe_embedding_model_id = uuid4()

    # Create mock models with security levels
    mock_completion_model = MagicMock(
        id=completion_model_id,
        security_level=MagicMock(value=100),  # Lower than new security level
    )
    mock_embedding_model = MagicMock(
        id=embedding_model_id,
        security_level=MagicMock(value=100),  # Lower than new security level
    )
    mock_safe_completion_model = MagicMock(
        id=safe_completion_model_id,
        security_level=MagicMock(value=200),  # Equal to new security level
    )
    mock_safe_embedding_model = MagicMock(
        id=safe_embedding_model_id,
        security_level=MagicMock(value=200),  # Equal to new security level
    )

    # Set up the mock space with the models
    mock_space = MagicMock(
        id=space_id,
        security_level=security_level,
        completion_models=[mock_completion_model, mock_safe_completion_model],
        embedding_models=[mock_embedding_model, mock_safe_embedding_model],
    )

    # Configure mock repository and service
    orchestrator_with_spaces.space_repo.get.return_value = mock_space
    orchestrator_with_spaces.security_level_service.get_security_level.return_value = (
        new_security_level
    )

    # Configure model access to return our models
    async def mock_get_completion_model(id: UUID, include_non_accessible: bool = False):
        if id == completion_model_id:
            return mock_completion_model
        elif id == safe_completion_model_id:
            return mock_safe_completion_model
        return None

    async def mock_get_embedding_model(id: UUID, include_non_accessible: bool = False):
        if id == embedding_model_id:
            return mock_embedding_model
        elif id == safe_embedding_model_id:
            return mock_safe_embedding_model
        return None

    orchestrator_with_spaces.model_access.get_completion_model = (
        mock_get_completion_model
    )
    orchestrator_with_spaces.model_access.get_embedding_model = mock_get_embedding_model

    # Execute
    result = await orchestrator_with_spaces.analyze_space_security_level_change(
        space_id=space_id,
        current_security_level=security_level,
        new_security_level=new_security_level,
    )

    # Verify
    assert result.affected_space is not None
    assert result.affected_space.space_id == space_id
    assert len(result.affected_space.new_completion_models) == 1
    assert len(result.affected_space.new_embedding_models) == 1
    assert mock_safe_completion_model in result.affected_space.new_completion_models
    assert mock_safe_embedding_model in result.affected_space.new_embedding_models
    assert mock_completion_model not in result.affected_space.new_completion_models
    assert mock_embedding_model not in result.affected_space.new_embedding_models
    assert result.warning is not None


async def test_analyze_space_security_level_change_no_current_level(
    orchestrator: SecurityLevelOrchestrator,
):
    """Test analyzing space security level changes when there is no current level."""
    # Setup
    space_id = uuid4()
    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=100,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Execute
    result = await orchestrator.analyze_space_security_level_change(
        space_id=space_id,
        current_security_level=None,
        new_security_level=new_security_level,
    )

    # Verify
    assert isinstance(result, SpaceSecurityAnalysisResponse)
    assert result.affected_space is None
    assert result.warning is None


async def test_update_space_security_level_with_impact(
    orchestrator_with_spaces: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test updating a space's security level that affects models."""
    # Setup
    space_id = uuid4()
    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=200,  # Higher security level
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Mock affected models
    completion_model_id = uuid4()
    embedding_model_id = uuid4()
    safe_completion_model_id = uuid4()
    safe_embedding_model_id = uuid4()

    # Create mock models with security levels
    mock_completion_model = MagicMock(
        id=completion_model_id,
        security_level=MagicMock(value=100),  # Lower than new security level
    )
    mock_embedding_model = MagicMock(
        id=embedding_model_id,
        security_level=MagicMock(value=100),  # Lower than new security level
    )
    mock_safe_completion_model = MagicMock(
        id=safe_completion_model_id,
        security_level=MagicMock(value=200),  # Equal to new security level
    )
    mock_safe_embedding_model = MagicMock(
        id=safe_embedding_model_id,
        security_level=MagicMock(value=200),  # Equal to new security level
    )

    # Set up the mock space with the models
    mock_space = MagicMock(
        id=space_id,
        security_level=security_level,
        completion_models=[mock_completion_model, mock_safe_completion_model],
        embedding_models=[mock_embedding_model, mock_safe_embedding_model],
    )

    # Create an updated space that will be returned after update
    updated_space = MagicMock(
        id=space_id,
        security_level=new_security_level,
        completion_models=[mock_safe_completion_model],
        embedding_models=[mock_safe_embedding_model],
    )

    # Configure mock repository and service
    orchestrator_with_spaces.space_repo.get.return_value = mock_space
    orchestrator_with_spaces.space_repo.update.return_value = updated_space
    orchestrator_with_spaces.security_level_service.get_security_level.return_value = (
        new_security_level
    )

    # Configure model access to return our models
    async def mock_get_completion_model(id: UUID, include_non_accessible: bool = False):
        if id == completion_model_id:
            return mock_completion_model
        elif id == safe_completion_model_id:
            return mock_safe_completion_model
        return None

    async def mock_get_embedding_model(id: UUID, include_non_accessible: bool = False):
        if id == embedding_model_id:
            return mock_embedding_model
        elif id == safe_embedding_model_id:
            return mock_safe_embedding_model
        return None

    orchestrator_with_spaces.model_access.get_completion_model = (
        mock_get_completion_model
    )
    orchestrator_with_spaces.model_access.get_embedding_model = mock_get_embedding_model

    # Execute
    result = await orchestrator_with_spaces.update_space_security_level(
        space_id=space_id,
        security_level_id=new_security_level.id,
    )

    # Verify
    assert result == updated_space
    assert result.security_level == new_security_level
    assert len(result.completion_models) == 1
    assert len(result.embedding_models) == 1
    assert mock_safe_completion_model in result.completion_models
    assert mock_safe_embedding_model in result.embedding_models
    assert mock_completion_model not in result.completion_models
    assert mock_embedding_model not in result.embedding_models


async def test_update_space_security_level_not_found(
    orchestrator: SecurityLevelOrchestrator,
):
    """Test updating a space's security level when space is not found."""
    # Setup
    space_id = uuid4()
    orchestrator.space_repo.get.return_value = None

    # Execute and verify
    with pytest.raises(NotFoundException) as exc:
        await orchestrator.update_space_security_level(
            space_id=space_id,
            security_level_id=uuid4(),
        )

    assert "Space not found" in str(exc.value)


async def test_analyze_security_level_change_space_not_found(
    orchestrator: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test analyzing security level changes when space is not found."""
    # Setup
    space_id = uuid4()
    orchestrator.space_repo.get.return_value = None
    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=200,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Execute
    result = await orchestrator._analyze_security_level_change(
        current_security_level=security_level,
        new_security_level=new_security_level,
        space_id=space_id,
    )

    # Verify
    assert isinstance(result, SecurityLevelChangeAnalysis)
    assert result.current_security_level == security_level
    assert result.new_security_level == new_security_level
    assert len(result.affected_spaces) == 0


async def test_analyze_security_level_change_no_current_level(
    orchestrator: SecurityLevelOrchestrator,
):
    """Test analyzing security level changes with no current security level."""
    # Setup
    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=100,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Execute
    result = await orchestrator._analyze_security_level_change(
        current_security_level=None,
        new_security_level=new_security_level,
        space_id=None,
    )

    # Verify
    assert isinstance(result, SecurityLevelChangeAnalysis)
    assert result.current_security_level is None
    assert result.new_security_level == new_security_level
    assert len(result.affected_spaces) == 0


async def test_analyze_models_for_security_level_basic(
    orchestrator: SecurityLevelOrchestrator,
):
    """Test basic model analysis with security levels."""
    # Setup
    model_id = uuid4()
    model = MagicMock(id=model_id, security_level=MagicMock(value=50))

    async def mock_get_model(id: UUID, include_non_accessible: bool = False):
        return model

    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=25,  # Lower security level - model should be available
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Execute
    available, unavailable = await orchestrator._analyze_models_for_security_level(
        models=[model],
        new_security_level=new_security_level,
        get_full_model_fn=mock_get_model,
    )

    # Verify
    assert len(available) == 1
    assert available[0] == model
    assert len(unavailable) == 0


async def test_analyze_models_for_security_level_unavailable(
    orchestrator: SecurityLevelOrchestrator,
):
    """Test model analysis when models become unavailable."""
    # Setup
    model_id = uuid4()
    model = MagicMock(id=model_id, security_level=MagicMock(value=25))

    async def mock_get_model(id: UUID, include_non_accessible: bool = False):
        return model

    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=50,  # Higher security level - model should be unavailable
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Execute
    available, unavailable = await orchestrator._analyze_models_for_security_level(
        models=[model],
        new_security_level=new_security_level,
        get_full_model_fn=mock_get_model,
    )

    # Verify
    assert len(available) == 0
    assert len(unavailable) == 1
    assert unavailable[0] == model


async def test_analyze_models_for_security_level_no_security_level(
    orchestrator: SecurityLevelOrchestrator,
):
    """Test model analysis when model has no security level."""
    # Setup
    model_id = uuid4()
    model = MagicMock(id=model_id, security_level=None)

    async def mock_get_model(id: UUID, include_non_accessible: bool = False):
        return model

    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=50,
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Execute
    available, unavailable = await orchestrator._analyze_models_for_security_level(
        models=[model],
        new_security_level=new_security_level,
        get_full_model_fn=mock_get_model,
    )

    # Verify
    assert len(available) == 0
    assert len(unavailable) == 1
    assert unavailable[0] == model


async def test_update_space_security_level_no_change(
    orchestrator: SecurityLevelOrchestrator,
):
    """Test updating space security level when no change is needed."""
    # Setup
    space_id = uuid4()
    security_level_id = uuid4()
    mock_space = MagicMock(
        id=space_id,
        security_level=MagicMock(id=security_level_id),
    )
    orchestrator.space_repo.get.return_value = mock_space

    # Execute
    result = await orchestrator.update_space_security_level(
        space_id=space_id,
        security_level_id=security_level_id,
    )

    # Verify
    assert result == mock_space
    orchestrator.space_repo.update.assert_not_called()


async def test_update_space_security_level_unaffected_space(
    orchestrator: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test updating space security level for an unaffected space."""
    # Setup
    space_id = uuid4()
    new_security_level = SecurityLevel(
        id=uuid4(),
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=50,  # Lower security level
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    mock_space = MagicMock(
        id=space_id,
        security_level=security_level,
        completion_models=[MagicMock(id=uuid4())],
        embedding_models=[MagicMock(id=uuid4())],
    )

    orchestrator.space_repo.get.return_value = mock_space
    orchestrator.security_level_service.get_security_level.return_value = (
        new_security_level
    )
    orchestrator.space_repo.update.return_value = mock_space

    # Execute
    result = await orchestrator.update_space_security_level(
        space_id=space_id,
        security_level_id=new_security_level.id,
    )

    # Verify
    assert result == mock_space
    assert result.completion_models == mock_space.completion_models
    assert result.embedding_models == mock_space.embedding_models


async def test_update_space_security_level_unaffected_keeps_models(
    orchestrator: SecurityLevelOrchestrator,
    security_level: SecurityLevel,
):
    """Test that an unaffected space keeps its current models when security level changes."""
    # Setup
    space_id = uuid4()
    new_security_level_id = uuid4()

    # Create mock models with security levels higher than new level
    completion_model = MagicMock()
    completion_model.id = uuid4()
    completion_model.security_level = MagicMock()
    completion_model.security_level.value = 50

    embedding_model = MagicMock()
    embedding_model.id = uuid4()
    embedding_model.security_level = MagicMock()
    embedding_model.security_level.value = 50

    # Create mock space with existing models
    mock_space = MagicMock()
    mock_space.id = space_id
    mock_space.security_level = security_level
    mock_space.completion_models = [completion_model]
    mock_space.embedding_models = [embedding_model]

    # Setup new security level with lower value (should not affect existing models)
    new_security_level = SecurityLevel(
        id=new_security_level_id,
        tenant_id=TEST_TENANT.id,
        name="new_level",
        description="New security level",
        value=25,  # Lower security level - won't affect existing models
        created_at=datetime(2024, 1, 1),
        updated_at=datetime(2024, 1, 1),
    )

    # Setup mock returns
    orchestrator.space_repo.get.return_value = mock_space
    orchestrator.security_level_service.get_security_level.return_value = (
        new_security_level
    )

    # Mock the model getter functions to return models with proper security levels
    async def mock_get_completion_model(id: UUID, include_non_accessible: bool = False):
        if id == completion_model.id:
            return completion_model
        return None

    async def mock_get_embedding_model(id: UUID, include_non_accessible: bool = False):
        if id == embedding_model.id:
            return embedding_model
        return None

    orchestrator.model_access.get_completion_model = mock_get_completion_model
    orchestrator.model_access.get_embedding_model = mock_get_embedding_model

    # Mock the update to return updated space
    updated_space = MagicMock()
    updated_space.id = space_id
    updated_space.security_level = new_security_level
    updated_space.completion_models = [completion_model]
    updated_space.embedding_models = [embedding_model]
    orchestrator.space_repo.update.return_value = updated_space

    # Execute
    result = await orchestrator.update_space_security_level(
        space_id=space_id,
        security_level_id=new_security_level_id,
    )

    # Verify
    mock_space.update.assert_called_once_with(
        security_level=new_security_level,
        completion_models=[completion_model],
        embedding_models=[embedding_model],
    )
    assert result == updated_space
    assert result.completion_models == [completion_model]
    assert result.embedding_models == [embedding_model]
    orchestrator.space_repo.update.assert_called_once_with(mock_space)
