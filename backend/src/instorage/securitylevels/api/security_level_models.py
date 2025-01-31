# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from instorage.main.models import InDB, partial_model


class SecurityLevelBase(BaseModel):
    """Base model for security level data."""

    name: str = Field(..., description="Name of the security level")
    description: Optional[str] = Field(
        None, description="Description of the security level"
    )
    value: int = Field(
        ..., description="Numeric value determining the security level hierarchy"
    )


class SecurityLevelCreatePublic(SecurityLevelBase):
    """Request model for creating a new security level."""
    pass


@partial_model
class SecurityLevelUpdatePublic(SecurityLevelCreatePublic):
    """Request model for updating an existing security level."""


class SecurityLevelSparse(InDB):
    """Basic security level information."""

    name: str
    description: Optional[str]
    value: int


class SecurityLevelPublic(BaseModel):
    """Public model for a security level."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    name: str
    description: Optional[str] = None
    value: int
    created_at: datetime
    updated_at: datetime
    warning: Optional[str] = None  # Warning message from impact analysis
