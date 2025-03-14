import asyncio

import pytest

from intric.main.config import SettingsProvider

def configure_test_setting(**kwargs):
    """Helper function to update test settings in tests"""
    return SettingsProvider.configure_for_testing(**kwargs)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
