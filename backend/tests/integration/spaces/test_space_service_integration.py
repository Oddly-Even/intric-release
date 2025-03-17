from intric.main.container.container import Container
from intric.securitylevels.security_level import SecurityLevel
from intric.spaces.space import Space


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


async def test_analyze_update_increased_security_level_from_no_security(
    container: Container,
    test_basic_space: Space,
    completion_model_factory,
    security_levels: list[SecurityLevel]
):
    """Test analyzing security level update for a space with no security level."""
    space_service = container.space_service()

    test_completion_model = await completion_model_factory(name="test-model", security_level_id=security_levels[0].id)
    # Add the completion model to the space
    await space_service.update_space(
        id=test_basic_space.id,
        completion_model_ids=[test_completion_model.id],
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


async def test_analyze_update_increased_security_level(
    container: Container,
    test_space_with_medium_security: Space,
    completion_model_factory,
    security_levels: list[SecurityLevel]
):
    """Test upgrading a space from medium security to high security."""
    space_service = container.space_service()

    test_completion_model = await completion_model_factory(name="test-model", security_level_id=security_levels[1].id)
    # Add the completion model to the space
    await space_service.update_space(
        id=test_space_with_medium_security.id,
        completion_model_ids=[test_completion_model.id],
        security_level_id=security_levels[1].id
    )

    # Analyze the update
    analysis = await space_service.analyze_update(
        test_space_with_medium_security.id,
        security_level_id=security_levels[2].id  # High security
    )

    assert analysis.current_security_level == security_levels[1]
    assert analysis.new_security_level == security_levels[2]
    assert(len(analysis.unavailable_completion_models) == 1)


async def test_analyze_update_decreased_security_level(
    container: Container,
    test_space_with_medium_security: Space,
    completion_model_factory,
    security_levels: list[SecurityLevel]
):
    """Test downgrading a space from high security to medium security."""
    space_service = container.space_service()

    test_completion_model = await completion_model_factory(name="test-model", security_level_id=security_levels[0].id)
    # Add the completion model to the space
    await space_service.update_space(
        id=test_space_with_medium_security.id,
        completion_model_ids=[test_completion_model.id],
        security_level_id=security_levels[1].id
    )

    # Analyze the update
    analysis = await space_service.analyze_update(
        test_space_with_medium_security.id,
        security_level_id=security_levels[0].id  # Low security
    )

    assert analysis.current_security_level == security_levels[1]
    assert analysis.new_security_level == security_levels[0]
    assert(len(analysis.unavailable_completion_models) == 0)
