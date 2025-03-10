import os
import subprocess
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from intric.main.config import Settings, get_settings


def setup_test_database():
    """Create test database and run migrations"""
    # Get base settings
    base_settings = get_settings()

    # Create test settings with overrides
    test_settings = Settings.model_validate({
        **base_settings.model_dump(),
        "testing": True,
        "postgres_db": f"{base_settings.postgres_db}_test"
    })

    # Connect to postgres to create/drop database
    conn = psycopg2.connect(
        host=test_settings.postgres_host,
        port=test_settings.postgres_port,
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
        dbname="postgres"  # Connect to default postgres db to create/drop databases
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()

    # Drop test database if it exists
    cursor.execute(f'DROP DATABASE IF EXISTS "{test_settings.postgres_db}"')
    print(f"Dropped database {test_settings.postgres_db} if it existed")

    # Create fresh test database
    cursor.execute(f'CREATE DATABASE "{test_settings.postgres_db}"')
    print(f"Created database {test_settings.postgres_db}")

    cursor.close()
    conn.close()

    # Set test environment for migrations
    os.environ["TESTING"] = "true"
    os.environ["POSTGRES_DB"] = base_settings.postgres_db  # Ensure original db name is used

    # Run migrations on test database
    backend_dir = Path(__file__).parent.parent.parent
    subprocess.run(
        ["poetry", "run", "alembic", "upgrade", "head"],
        check=True,
        cwd=backend_dir,
        env={**os.environ, "TESTING": "true"},
    )
    print("Ran migrations successfully")


if __name__ == "__main__":
    setup_test_database()
