"""
Space-specific test fixtures.
These fixtures are specific to space functionality and are used by space-related tests.
"""

import pytest
from intric.main.container.container import Container
from intric.securitylevels.security_level import SecurityLevel
from intric.spaces.space import Space


@pytest.fixture
async def test_basic_space(db_session, container: Container) -> Space:
    """Create a basic space for testing.

    This is the base fixture for space tests. Other fixtures can build upon this
    to create more specialized space configurations.
    """
    space_service = container.space_service()
    async with db_session.begin():
        new_space = await space_service.create_space(name="Test Space")

    return new_space


@pytest.fixture
async def test_space_with_low_security(
    db_session,
    container: Container,
    test_basic_space: Space,
    security_levels: list[SecurityLevel]
) -> Space:
    """Create a space with security level configured.

    This fixture takes the basic space and adds a security level to it.
    """
    space_service = container.space_service()
    async with db_session.begin():
        await space_service.update_space(
            id=test_basic_space.id,
            security_level_id=security_levels[0].id  # Low security
        )
    return await space_service.get_space(test_basic_space.id)

@pytest.fixture
async def test_space_with_medium_security(
    db_session,
    container: Container,
    test_basic_space: Space,
    security_levels: list[SecurityLevel]
) -> Space:
    """Create a space with medium security level configured.

    This fixture takes the basic space and adds a medium security level to it.
    """
    space_service = container.space_service()
    async with db_session.begin():
        await space_service.update_space(
            id=test_basic_space.id,
            security_level_id=security_levels[1].id  # Medium security
        )
    return await space_service.get_space(test_basic_space.id)
