# Copyright (c) 2024 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import Optional
from uuid import UUID

from instorage.main.exceptions import BadRequestException, NotFoundException
from instorage.roles.permissions import Permission, validate_permissions
from instorage.securitylevels.security_level import SecurityLevel, SecurityLevelCreate, SecurityLevelUpdate
from instorage.securitylevels.security_level_repo import SecurityLevelRepository
from instorage.users.user import UserInDB


class SecurityLevelService:
    """Service for managing security levels."""

    def __init__(
        self,
        user: UserInDB,
        repo: SecurityLevelRepository,
    ):
        self.user = user
        self.repo = repo

    async def _get_security_level(self, id: UUID) -> SecurityLevel:
        """Get a security level and validate access."""
        security_level = await self.repo.get(id)
        if not security_level:
            raise NotFoundException(f"Security level with id '{id}' not found")
        return security_level

    @validate_permissions(Permission.ADMIN)
    async def create_security_level(
        self, name: str, description: Optional[str], value: int
    ) -> SecurityLevel:
        """Create a new security level."""
        # Check if name already exists
        existing = await self.repo.get_by_name(name)
        if existing:
            raise BadRequestException(f"Security level with name '{name}' already exists")

        # Create security level
        security_level = SecurityLevelCreate(
            name=name,
            description=description,
            value=value,
        )
        
        # Save to database
        return await self.repo.create(security_level)

    async def get_security_level(self, id: UUID) -> SecurityLevel:
        """Get a security level by ID."""
        return await self._get_security_level(id)

    async def get_security_level_by_name(self, name: str) -> Optional[SecurityLevel]:
        """Get a security level by name."""
        return await self.repo.get_by_name(name)

    async def list_security_levels(self) -> list[SecurityLevel]:
        """List all security levels ordered by value."""
        return await self.repo.list_all()

    @validate_permissions(Permission.ADMIN)
    async def update_security_level(
        self,
        id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        value: Optional[int] = None,
    ) -> SecurityLevel:
        """Update a security level."""
        security_level = await self._get_security_level(id)

        # Check if name already exists if updating name
        if name:
            existing = await self.repo.get_by_name(name)
            if existing and existing.id != id:
                raise BadRequestException(f"Security level with name '{name}' already exists")

        # Create update model
        update = SecurityLevelUpdate(
            id=id,
            name=name if name is not None else security_level.name,
            description=description if description is not None else security_level.description,
            value=value if value is not None else security_level.value,
        )

        return await self.repo.update(update)

    @validate_permissions(Permission.ADMIN)
    async def delete_security_level(self, id: UUID) -> None:
        """Delete a security level."""
        security_level = await self._get_security_level(id)
        await self.repo.delete(security_level.id)

    async def validate_security_level(
        self, required_level: SecurityLevel, provided_level: SecurityLevel
    ) -> bool:
        """Validate if a provided security level meets the required level."""
        return provided_level.value >= required_level.value

    async def get_highest_security_level(self) -> Optional[int]:
        """Get the highest security level value."""
        return await self.repo.get_highest_value() 
