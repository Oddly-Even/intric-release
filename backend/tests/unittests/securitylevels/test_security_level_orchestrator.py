from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from instorage.main.exceptions import BadRequestException, NotFoundException
from instorage.securitylevels.security_level import SecurityLevel
from instorage.securitylevels.security_level_orchestrator import (
    SecurityLevelOrchestrator,
    SecurityLevelResponse,
    SpaceSecurityAnalysisResponse,
)
from instorage.securitylevels.security_level_analysis import SecurityLevelAnalysis
from tests.fixtures import TEST_UUID, TEST_TENANT, TEST_USER
from tests.unittests.securitylevels.test_security_level_analysis import (
    security_levels,
    models,
    spaces,
)


@pytest.fixture
def mock_service():
    """Create a mock security level service."""
    service = AsyncMock()
    return service


@pytest.fixture
def mock_completion_model_repo():
    """Create a mock completion model repository."""
    repo = AsyncMock()
    repo.get_model.return_value = None
    repo.set_completion_model_security_level = AsyncMock()
    return repo


@pytest.fixture
def mock_embedding_model_repo():
    """Create a mock embedding model repository."""
    repo = AsyncMock()
    repo.get_model.return_value = None
    repo.set_embedding_model_security_level = AsyncMock()
    return repo


@pytest.fixture
def mock_space_repo():
    """Create a mock space repository."""
    repo = AsyncMock()
    repo.get.return_value = None
    repo.update = AsyncMock()
    repo.get_spaces_by_security_level = AsyncMock(return_value=[])
    repo.get_spaces_by_completion_model = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def orchestrator(mock_service, mock_completion_model_repo, mock_embedding_model_repo, mock_space_repo):
    """Create an orchestrator instance for testing."""
    return SecurityLevelOrchestrator(
        user=TEST_USER,
        security_level_service=mock_service,
        completion_model_repo=mock_completion_model_repo,
        embedding_model_repo=mock_embedding_model_repo,
        space_repo=mock_space_repo,
    )


async def test_create_security_level_no_impact(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
):
    """Test creating a security level with no impact."""
    # Setup
    new_security_level = security_levels["low"]
    orchestrator.security_level_service.create_security_level.return_value = new_security_level
    orchestrator.space_repo.get_spaces_by_security_level.return_value = []

    # Execute
    result = await orchestrator.create_security_level(
        name="test_level",
        description="Test security level",
        value=25,
    )

    # Verify
    assert isinstance(result, SecurityLevelResponse)
    assert result.security_level == new_security_level
    assert result.warning is None
    orchestrator.security_level_service.create_security_level.assert_called_once_with(
        name="test_level",
        description="Test security level",
        value=25,
    )


async def test_create_security_level_with_impact(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
    spaces,
):
    """Test creating a security level that affects existing spaces."""
    # Setup
    new_security_level = security_levels["high"]  # High security level will affect spaces
    orchestrator.security_level_service.create_security_level.return_value = new_security_level
    
    # Configure space repo to return affected spaces
    orchestrator.space_repo.get_spaces_by_security_level.return_value = [
        spaces["low_security"]
    ]

    # Execute
    result = await orchestrator.create_security_level(
        name="high_security",
        description="High security level",
        value=75,
    )

    # Verify
    assert isinstance(result, SecurityLevelResponse)
    assert result.security_level == new_security_level
    assert result.warning is not None
    assert "spaces will be affected" in result.warning


async def test_update_security_level_no_impact(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
):
    """Test updating a security level with no impact."""
    # Setup
    current_level = security_levels["low"]
    orchestrator.security_level_service.get_security_level.return_value = current_level
    orchestrator.security_level_service.update_security_level.return_value = current_level
    orchestrator.space_repo.get_spaces_by_security_level.return_value = []

    # Execute
    result = await orchestrator.update_security_level(
        id=current_level.id,
        name="updated_name",
        description="Updated description",
    )

    # Verify
    assert isinstance(result, SecurityLevelResponse)
    assert result.security_level == current_level
    assert result.warning is None


async def test_update_security_level_with_impact(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
    spaces,
):
    """Test updating a security level that affects existing spaces."""
    # Setup
    current_level = security_levels["low"]
    updated_level = SecurityLevel(
        id=current_level.id,
        tenant_id=current_level.tenant_id,
        name=current_level.name,
        description=current_level.description,
        value=75,  # Increased value
        created_at=current_level.created_at,
        updated_at=current_level.updated_at,
    )
    
    orchestrator.security_level_service.get_security_level.return_value = current_level
    orchestrator.security_level_service.update_security_level.return_value = updated_level
    orchestrator.space_repo.get_spaces_by_security_level.return_value = [
        spaces["low_security"]
    ]

    # Execute
    result = await orchestrator.update_security_level(
        id=current_level.id,
        value=75,  # Increase security level
    )

    # Verify
    assert isinstance(result, SecurityLevelResponse)
    assert result.security_level == updated_level
    assert result.warning is not None
    assert "spaces will be affected" in result.warning


async def test_delete_security_level_no_impact(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
):
    """Test deleting a security level with no impact."""
    # Setup
    security_level = security_levels["low"]
    orchestrator.security_level_service.get_security_level.return_value = security_level
    orchestrator.space_repo.get_spaces_by_security_level.return_value = []

    # Execute
    result = await orchestrator.delete_security_level(security_level.id)

    # Verify
    assert isinstance(result, SecurityLevelAnalysis)
    assert not result.has_changes
    assert result.total_affected_spaces == 0
    assert len(result.space_analyses) == 0
    orchestrator.security_level_service.delete_security_level.assert_called_once_with(
        security_level.id
    )


async def test_delete_security_level_with_impact(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
    spaces,
):
    """Test deleting a security level that is in use."""
    # Setup
    security_level = security_levels["low"]
    orchestrator.security_level_service.get_security_level.return_value = security_level
    orchestrator.space_repo.get_spaces_by_security_level.return_value = [
        spaces["low_security"]
    ]

    # Execute
    result = await orchestrator.delete_security_level(security_level.id)

    # Verify
    assert isinstance(result, SecurityLevelAnalysis)
    assert result.has_changes
    assert result.total_affected_spaces == 1
    assert len(result.space_analyses) == 1
    assert result.space_analyses[0].space_id == spaces["low_security"].id
    orchestrator.security_level_service.delete_security_level.assert_not_called()


async def test_analyze_security_level_update(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
    spaces,
):
    """Test analyzing security level updates."""
    # Setup
    current_level = security_levels["low"]
    orchestrator.security_level_service.get_security_level.return_value = current_level
    orchestrator.space_repo.get_spaces_by_security_level.return_value = [
        spaces["low_security"]
    ]

    # Execute
    analysis = await orchestrator.analyze_security_level_update(
        id=current_level.id,
        value=75,  # Higher security level
    )

    # Verify
    assert isinstance(analysis, SecurityLevelAnalysis)
    assert analysis.has_changes
    assert analysis.total_affected_spaces == 1
    assert len(analysis.space_analyses) == 1
    assert analysis.space_analyses[0].space_id == spaces["low_security"].id


async def test_analyze_space_security_level_change(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
    spaces,
):
    """Test analyzing space security level changes."""
    # Setup
    space = spaces["low_security"]
    new_security_level = security_levels["high"]
    orchestrator.security_level_service.get_security_level.return_value = new_security_level

    # Execute
    analysis = await orchestrator.analyze_space_security_level_change(
        space_id=space.id,
        security_level_id=new_security_level.id,
    )

    # Verify
    assert isinstance(analysis, SecurityLevelAnalysis)
    assert analysis.has_changes
    assert analysis.total_affected_spaces == 1
    assert len(analysis.space_analyses) == 1
    assert analysis.space_analyses[0].space_id == space.id


async def test_update_space_security_level(
    orchestrator: SecurityLevelOrchestrator,
    security_levels,
    spaces,
):
    """Test updating space security level."""
    # Setup
    space = spaces["low_security"]
    new_security_level = security_levels["high"]
    orchestrator.security_level_service.get_security_level.return_value = new_security_level
    orchestrator.space_repo.get.return_value = space

    # Execute
    analysis = await orchestrator.update_space_security_level(
        space_id=space.id,
        security_level_id=new_security_level.id,
    )

    # Verify
    assert isinstance(analysis, SecurityLevelAnalysis)
    assert analysis.has_changes
    assert analysis.total_affected_spaces == 1
    assert len(analysis.space_analyses) == 1
    assert analysis.space_analyses[0].space_id == space.id
    orchestrator.space_repo.update.assert_called_once()


async def test_update_space_security_level_not_found(
    orchestrator: SecurityLevelOrchestrator,
):
    """Test updating a space's security level when space is not found."""
    # Setup
    orchestrator.space_repo.get.return_value = None

    # Execute and verify
    with pytest.raises(NotFoundException) as exc:
        await orchestrator.update_space_security_level(
            space_id=uuid4(),
            security_level_id=uuid4(),
        )

    assert "Space not found" in str(exc.value) 