from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from instorage.main.models import InDB, partial_model


class CreateRequest(BaseModel):
    """Base model for creating a security level."""
    name: str = Field(..., description="Name of the security level")
    description: Optional[str] = Field(None, description="Description of the security level")
    value: int = Field(..., description="Numeric value determining the security level hierarchy")


class CreateSecurityLevelRequest(CreateRequest):
    """Request model for creating a new security level."""
    pass


@partial_model
class UpdateSecurityLevelRequest(BaseModel):
    """Request model for updating an existing security level."""
    name: Optional[str] = Field(None, description="Name of the security level")
    description: Optional[str] = Field(None, description="Description of the security level")
    value: Optional[int] = Field(None, description="Numeric value determining the security level hierarchy")


class SecurityLevelSparse(InDB):
    """Basic security level information."""
    name: str
    description: Optional[str]
    value: int


class SecurityLevelPublic(SecurityLevelSparse):
    """Complete security level information including relationships."""
    pass  # We'll add relationships to AI models later when implementing that part 