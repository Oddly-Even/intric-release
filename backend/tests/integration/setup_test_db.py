import os
import subprocess
from pathlib import Path

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from intric.main.config import Settings, SettingsProvider, SETTINGS


def setup_test_database():
    """Create test database and run migrations"""
    # Get base settings
    settings = SettingsProvider.configure_for_testing()

    # Connect to postgres to create/drop database
    conn = psycopg2.connect(
        host=settings.postgres_host,
        port=settings.postgres_port,
        user=settings.postgres_user,
        password=settings.postgres_password,
        dbname="postgres"  # Connect to default postgres db to create/drop databases
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    cursor = conn.cursor()

    # Drop test database if it exists
    cursor.execute(f'DROP DATABASE IF EXISTS "{settings.postgres_db}"')
    print(f"Dropped database {settings.postgres_db} if it existed")

    # Create fresh test database
    cursor.execute(f'CREATE DATABASE "{settings.postgres_db}"')
    print(f"Created database {settings.postgres_db}")

    cursor.close()
    conn.close()

    # Set test environment for migrations
    os.environ["TESTING"] = "true"
    os.environ["POSTGRES_DB"] = settings.postgres_db  # Ensure original db name is used

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
