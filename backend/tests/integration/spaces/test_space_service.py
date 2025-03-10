import pytest
from intric.main.container.container import Container
from intric.securitylevels.security_level import SecurityLevel
from intric.spaces.space import Space
from intric.ai_models.completion_models.completion_model import CompletionModel

@pytest.mark.asyncio
async def test_create_additional_space(container: Container, test_basic_space: Space):
    """Test creating an additional space when we already have a basic one."""
    # Verify the fixture-created space
    assert test_basic_space.name == "Test Space"
    assert container.user().id in test_basic_space.members

    # Create another space
    space_service = container.space_service()
    another_space = await space_service.create_space(name="Another Test Space")

    # Verify the new space
    assert another_space.name == "Another Test Space"
    assert container.user().id in another_space.members
    assert another_space.id != test_basic_space.id


@pytest.mark.asyncio
async def test_analyze_security_update(
    container: Container,
    test_basic_space: Space,
    completion_model_factory,
    security_levels: list[SecurityLevel]
):
    """Test analyzing security level update for a space."""
    space_service = container.space_service()

    test_completion_model = await completion_model_factory(name="test-model", security_level_id=security_levels[0].id)
    # Add the completion model to the space
    await space_service.update_space(
        id=test_basic_space.id,
        completion_model_ids=[test_completion_model.id]
    )
    # Analyze the update
    analysis = await space_service.analyze_update(
        test_basic_space.id,
        security_level_id=security_levels[1].id  # Medium security
    )

    assert analysis.current_security_level is None
    assert analysis.new_security_level == security_levels[1]
    assert(len(analysis.unavailable_completion_models) == 1)
    assert(analysis.unavailable_completion_models[0].id == test_completion_model.id)

@pytest.mark.asyncio
async def test_space_with_security(test_space_with_security: Space):
    """Test space with security level already configured."""
    assert test_space_with_security.security_level is not None
    assert test_space_with_security.security_level.value == 1  # Low security
