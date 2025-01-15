# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from instorage.database.tables.base_class import BasePublic
from instorage.database.tables.tenant_table import Tenants

if TYPE_CHECKING:
    from instorage.database.tables.ai_models_table import CompletionModelSettings, EmbeddingModelSettings
    from instorage.database.tables.spaces_table import Spaces


class SecurityLevels(BasePublic):
    """Table for storing security levels."""

    # Core fields
    name: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    value: Mapped[int] = mapped_column()

    # Tenant relationship
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(Tenants.id, ondelete="CASCADE"),
        nullable=False,
    )
    tenant: Mapped["Tenants"] = relationship()

    # Relationships
    completion_model_settings: Mapped[list["CompletionModelSettings"]] = relationship(
        back_populates="security_level",
        order_by="CompletionModelSettings.created_at"
    )
    embedding_model_settings: Mapped[list["EmbeddingModelSettings"]] = relationship(
        back_populates="security_level",
        order_by="EmbeddingModelSettings.created_at"
    )
    spaces: Mapped[list["Spaces"]] = relationship(
        back_populates="security_level",
        order_by="Spaces.created_at"
    )
