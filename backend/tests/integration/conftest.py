# Integration Test Fixtures
# This file contains core fixtures used across multiple integration tests.
#
# Fixture Placement Strategy:
# 1. Core infrastructure fixtures belong here (db_session, container)
# 2. Base entity fixtures used widely belong here (test_tenant, test_user)
# 3. Domain-specific fixtures should go in their respective fixtures.py files
# 4. One-off fixtures should stay in their test files
#
# Naming Convention:
# - Prefix integration fixtures with 'test_' to avoid conflicts with unit test fixtures
# - Use clear, descriptive names that indicate the fixture's purpose

import asyncio
from typing import AsyncGenerator

import bcrypt
import pytest
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from intric.database.database import sessionmanager
from intric.main.config import get_settings
from intric.main.container.container import Container
from intric.users.user import UserInDB
from intric.tenants.tenant import TenantInDB
from intric.securitylevels.security_level import SecurityLevel
from intric.ai_models.completion_models.completion_model import CompletionModel
from intric.spaces.space import Space


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    """Initialize database for testing"""
    # Initialize the database with test configuration
    settings = get_settings()
    sessionmanager.init(settings.database_url)

    yield

    # Cleanup
    await sessionmanager.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for testing"""
    async with sessionmanager.session() as session:
        # Start a transaction
        async with session.begin():
            # Give the session to the test
            yield session
            # Rollback the transaction after the test
            await session.rollback()


def hash_password(password: str) -> tuple[str, str]:
    """Hash a password for storing."""
    salt = bcrypt.gensalt().decode()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password + salt), salt


@pytest.fixture
async def test_tenant(db_session: AsyncSession) -> TenantInDB:
    """Create a test tenant."""
    # Insert tenant
    result = await db_session.execute(
        text("""
        INSERT INTO tenants (name, quota_limit)
        VALUES ('TestTenant', '10737418240')
        RETURNING id, name, quota_limit, created_at, updated_at
        """)
    )
    tenant_row = result.fetchone()

    return TenantInDB(
        id=tenant_row[0],
        name=tenant_row[1],
        quota_limit=tenant_row[2],
        created_at=tenant_row[3],
        updated_at=tenant_row[4]
    )


@pytest.fixture
async def test_user(db_session: AsyncSession, test_tenant: TenantInDB) -> UserInDB:
    """Create a test user with owner role."""
    # Create user
    hashed_pass, salt = hash_password("TestPass123!")
    result = await db_session.execute(
        text("""
        INSERT INTO users (username, email, password, salt, tenant_id, used_tokens, state)
        VALUES ('testuser', 'test@example.com', :password, :salt, :tenant_id, 0, 'active')
        RETURNING id, username, email, tenant_id, used_tokens, state, created_at, updated_at
        """),
        {"password": hashed_pass, "salt": salt, "tenant_id": test_tenant.id}
    )
    user_row = result.fetchone()

    # Create owner role if it doesn't exist
    result = await db_session.execute(
        text("""
        INSERT INTO predefined_roles (name, permissions)
        VALUES ('Owner', ARRAY['admin', 'assistants', 'services', 'collections', 'insights', 'AI', 'editor', 'websites'])
        ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
        RETURNING id
        """)
    )
    role_id = result.fetchone()[0]

    # Assign role to user
    await db_session.execute(
        text("""
        INSERT INTO users_predefined_roles (user_id, predefined_role_id)
        VALUES (:user_id, :role_id)
        ON CONFLICT DO NOTHING
        """),
        {"user_id": user_row[0], "role_id": role_id}
    )

    return UserInDB(
        id=user_row[0],
        username=user_row[1],
        email=user_row[2],
        tenant_id=user_row[3],
        used_tokens=user_row[4],
        state=user_row[5],
        created_at=user_row[6],
        updated_at=user_row[7],
        tenant=test_tenant
    )

@pytest.fixture
async def security_levels(db_session: AsyncSession, test_tenant: TenantInDB) -> list[SecurityLevel]:
    """Create three security levels with ascending values."""
    levels = []
    for i, (name, value) in enumerate([
        ("Low Security", 1),
        ("Medium Security", 2),
        ("High Security", 3)
    ]):
        result = await db_session.execute(
            text("""
            INSERT INTO security_levels (name, description, value, tenant_id)
            VALUES (:name, :description, :value, :tenant_id)
            RETURNING id, name, description, value, tenant_id, created_at, updated_at
            """),
            {
                "name": name,
                "description": f"Security level {value}",
                "value": value,
                "tenant_id": test_tenant.id
            }
        )
        level_row = result.fetchone()

        levels.append(SecurityLevel(
            id=level_row[0],
            name=level_row[1],
            description=level_row[2],
            value=level_row[3],
            tenant_id=level_row[4],
            created_at=level_row[5],
            updated_at=level_row[6]
        ))

    return levels

@pytest.fixture
async def test_completion_model(completion_model_factory) -> CompletionModel:
    """Create a default test completion model using the factory."""
    return await completion_model_factory(name="test-model")

@pytest.fixture
async def container(
    db_session: AsyncSession,
    test_user: UserInDB,
    test_tenant: TenantInDB,
) -> Container:
    """Create a configured container with test dependencies.

    This container comes pre-configured with:
    - Database session
    - Test user (with owner role)
    - Test tenant
    - A default test completion model
    """
    container = Container()
    container.session.override(db_session)
    container.user.override(test_user)
    container.tenant.override(test_tenant)
    return container


@pytest.fixture
def completion_model_factory(db_session, test_tenant, test_user, security_levels):
    """Factory for creating CompletionModel instances with customizable properties.

    Usage:
    ```python
    async def test_example(completion_model_factory):
        model = await completion_model_factory(
            name="test-model-custom",
            family="anthropic"
        )
        # Use model in tests...
    ```
    """
    from uuid import uuid4

    async def _create_model(
        name=None,
        nickname=None,
        family="openai",
        token_limit=128000,
        stability="stable",
        hosting="usa",
        is_deprecated=False,
        vision=True,
        open_source=False,
        security_level_id=None
    ):
        # Generate unique name if not provided
        if name is None:
            name = f"test-model-{uuid4()}"
        if nickname is None:
            nickname = f"Test Model {name.split('-')[-1]}"

        # Create model in database
        result = await db_session.execute(
            text("""
            INSERT INTO completion_models (
                name, nickname, family, token_limit, stability, hosting,
                description, vision, is_deprecated, open_source
            )
            VALUES (
                :name, :nickname, :family, :token_limit, :stability, :hosting,
                :description, :vision, :is_deprecated, :open_source
            )
            RETURNING id, name, nickname, token_limit, family, stability, hosting,
                    description, org, vision, is_deprecated, created_at, updated_at
            """),
            {
                "name": name,
                "nickname": nickname,
                "family": family,
                "token_limit": token_limit,
                "stability": stability,
                "hosting": hosting,
                "description": f"Test model {name} for integration tests",
                "vision": vision,
                "is_deprecated": is_deprecated,
                "open_source": open_source
            }
        )
        model_row = result.fetchone()

        # Create settings for the tenant
        await db_session.execute(
            text("""
            INSERT INTO completion_model_settings (
                tenant_id, completion_model_id, is_org_enabled, is_org_default, security_level_id
            )
            VALUES (:tenant_id, :model_id, TRUE, TRUE, :security_level_id)
            """),
            {
                "tenant_id": test_tenant.id,
                "model_id": model_row[0],
                "security_level_id": security_level_id
            }
        )

        # Create and return model instance
        return CompletionModel(
            user=test_user,
            id=model_row[0],
            name=model_row[1],
            nickname=model_row[2],
            token_limit=model_row[3],
            family=model_row[4],
            stability=model_row[5],
            hosting=model_row[6],
            description=model_row[7],
            org=model_row[8],
            vision=model_row[9],
            is_deprecated=model_row[10],
            created_at=model_row[11],
            updated_at=model_row[12],
            model_name=model_row[1],
            open_source=open_source,
            nr_billion_parameters=None,
            hf_link=None,
            deployment_name=None,
            is_org_enabled=True,
            is_org_default=True,
            security_level_id=security_level_id
        )

    return _create_model


@pytest.fixture
def space_factory(container):
    """Factory for creating Space instances with customizable properties.

    Usage:
    ```python
    async def test_example(space_factory, completion_model_factory):
        model = await completion_model_factory()
        space = await space_factory(
            name="Custom Space",
            completion_model_ids=[model.id]
        )
        # Use space in tests...
    ```
    """
    from uuid import uuid4

    async def _create_space(
        name=None,
        description=None,
        security_level_id=None,
        completion_model_ids=None
    ):
        space_service = container.space_service()

        # Generate a unique name if not provided
        if name is None:
            name = f"Test Space {uuid4()}"

        # Create the space
        space = await space_service.create_space(
            name=name,
            description=description
        )

        # Apply additional configurations if provided
        update_params = {}

        if security_level_id is not None:
            update_params["security_level_id"] = security_level_id

        if completion_model_ids is not None:
            update_params["completion_model_ids"] = completion_model_ids

        if update_params:
            await space_service.update_space(
                id=space.id,
                **update_params
            )
            # Reload the space to get updated properties
            space = await space_service.get_space(space.id)

        return space

    return _create_space


@pytest.fixture
async def test_basic_space(space_factory) -> Space:
    """Create a basic space for testing using the space factory."""
    return await space_factory(name="Test Space")
