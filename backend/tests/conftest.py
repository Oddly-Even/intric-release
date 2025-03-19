import asyncio
import pytest
from intric.main.config import get_settings, SETTINGS

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def test_settings():
    """Set test settings."""
    SETTINGS.postgres_db = "postgres_test"
    yield SETTINGS


@pytest.fixture(scope="session", autouse=True)
def verify_test_settings(test_settings):
    """Verify that test settings are active before running any tests."""
    current_settings = get_settings()
    assert current_settings.postgres_db == "postgres_test", (
        "Test settings are not active! Tests must be run with test configuration.")
