import pytest
import subprocess
from intric.database.database import sessionmanager
from sqlalchemy import text
from intric.server.main import get_application
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from contextlib import ExitStack
from intric.database.database import AsyncSession
from typing import AsyncGenerator
from intric.server.dependencies.container import Container
from init_db import add_tenant_user
import psycopg2
import os
from pathlib import Path
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


@pytest.fixture
def app():
    """Create a test FastAPI application."""
    with ExitStack():
        test_app = get_application()
        yield test_app

@pytest.fixture
async def test_client(app: FastAPI):
    """Create a test client for the FastAPI app."""
    async with AsyncClient(base_url="http://test", transport=ASGITransport(app), follow_redirects=True) as client:
        yield client

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with sessionmanager.session() as session:
        yield session

@pytest.fixture(scope="function", autouse=True)
async def create_basic_data(test_settings):
    """
    Create basic data for the test. For example a tenant, a user and roles.
    """

    # Create a direct database connection for the add_tenant_user function
    conn = psycopg2.connect(
        host=test_settings.postgres_host,
        port=test_settings.postgres_port,
        dbname=test_settings.postgres_db,  # Use test database
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
    )

    tenant_name = "TestTenant"
    quota_limit = "10737418240"  # 10GB in bytes
    user_name = "TestUser"
    user_email = "test@example.com"
    user_password = "TestPassword123!"

    add_tenant_user(
        conn=conn,
        tenant_name=tenant_name,
        quota_limit=quota_limit,
        user_name=user_name,
        user_email=user_email,
        user_password=user_password,
    )

    conn.close()

@pytest.fixture(scope="function")
async def container(db_session):
    container = Container()
    container.session.override(db_session)
    async with container.session().begin():
        tenants = await container.tenant_service().get_all_tenants(domain=None)
        test_tenant = next(tenant for tenant in tenants if tenant.name == "TestTenant")
        users = await container.user_service().get_all_users(tenant_id=test_tenant.id)
        test_user = next(user for user in users if user.email == "test@example.com")

    container.user.override(test_user)
    container.tenant.override(test_tenant)

    return container

@pytest.fixture(scope="session", autouse=True)
async def setup_database(test_settings):
    """Setup test database including migrations"""
    print(f"Using host: {test_settings.postgres_host}, port: {test_settings.postgres_port}, user: {test_settings.postgres_user}")

    setup_test_database(test_settings)

    sessionmanager.init(test_settings.database_url)

    yield

    await sessionmanager.close()

@pytest.fixture(autouse=True)
async def clean_database():
    """Truncate all tables between tests to ensure a clean state."""
    # Run test first
    yield

    # Clean up database AFTER test completes
    # This will use a separate session from the test session
    print("Cleaning database after test...")
    async with sessionmanager.session() as session:
        async with session.begin():
            # Get the current database schema (usually 'public')
            result = await session.execute(text("SELECT current_schema()"))
            schema = result.scalar()

            # Disable foreign key constraints temporarily for clean truncation
            await session.execute(text("SET session_replication_role = 'replica';"))

            # Get a list of all tables in the schema
            result = await session.execute(
                text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = :schema
                AND tablename != 'alembic_version'  -- Keep migration tracking
                """),
                {"schema": schema}
            )
            tables = [row[0] for row in result.fetchall()]

            if tables:
                # Format for TRUNCATE statement
                tables_str = ', '.join(f'"{t}"' for t in tables)

                # Truncate all tables in one statement
                await session.execute(text(f"TRUNCATE TABLE {tables_str} CASCADE"))
                print(f"Truncated {len(tables)} tables")

            # Re-enable foreign key constraints
            await session.execute(text("SET session_replication_role = 'origin';"))

def user_token(container):
    """Generate a JWT token for a user."""
    return container.auth_service().create_access_token_for_user(container.user())


def setup_test_database(settings):
    """Create test database and run migrations"""

    # Connect to postgres to create/drop database
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        dbname="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()

    # Drop test database if it exists
    print(f"Dropping database {settings.postgres_db} if it existed")
    cursor.execute(f'DROP DATABASE IF EXISTS "{settings.postgres_db}"')
    print(f"Dropped database {settings.postgres_db} if it existed")

    # Create fresh test database
    cursor.execute(f'CREATE DATABASE "{settings.postgres_db}"')
    print(f"Created database {settings.postgres_db}")

    cursor.close()
    conn.close()

    # Run migrations on test database
    backend_dir = Path(__file__).parent.parent.parent
    subprocess.run(
        ["poetry", "run", "alembic", "upgrade", "head"],
        check=True,
        cwd=backend_dir,
        env=os.environ,
    )
    print("Ran migrations successfully")
