# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from instorage.database.repositories.base import BaseRepositoryDelegate
from instorage.database.tables.security_levels_table import SecurityLevels
from instorage.securitylevels.security_level import (
    SecurityLevel,
    SecurityLevelCreate,
    SecurityLevelUpdate,
)


class SecurityLevelRepository:
    """Repository for managing security levels."""

    def __init__(self, session: AsyncSession):
        self.delegate = BaseRepositoryDelegate(
            session,
            SecurityLevels,
            SecurityLevel,
        )
        self.session = session

    async def create(self, security_level: SecurityLevelCreate) -> SecurityLevel:
        """Create a new security level."""
        return await self.delegate.add(security_level)

    async def get(self, id: UUID) -> Optional[SecurityLevel]:
        """Get a security level by ID."""
        return await self.delegate.get(id)

    async def get_by_name(self, name: str) -> Optional[SecurityLevel]:
        """Get a security level by name."""
        query = sa.select(SecurityLevels).where(SecurityLevels.name == name)
        return await self.delegate.get_model_from_query(query)

    async def list_all(self) -> list[SecurityLevel]:
        """List all security levels ordered by value."""
        query = sa.select(SecurityLevels).order_by(SecurityLevels.value)
        return await self.delegate.get_models_from_query(query)

    async def update(self, security_level: SecurityLevelUpdate) -> SecurityLevel:
        """Update an existing security level."""
        return await self.delegate.update(security_level)

    async def delete(self, id: UUID) -> bool:
        """Delete a security level."""
        await self.delegate.delete(id)
        return True

    async def get_highest_value(self) -> Optional[int]:
        """Get the highest security level value."""
        stmt = sa.select(SecurityLevels.value).order_by(SecurityLevels.value.desc())
        result = await self.session.execute(stmt)
        value = result.scalar_one_or_none()
        return value
