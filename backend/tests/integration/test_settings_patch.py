import pytest

def test_settings_patch_applied():
    """Test that verifies the monkey patch is applied correctly."""
    from intric.main.config import get_settings

    settings = get_settings()
    assert settings.postgres_db == "postgres_test"  # Check a test-specific value
    print("Settings patch verified!")
