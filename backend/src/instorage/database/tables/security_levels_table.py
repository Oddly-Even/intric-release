# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from instorage.database.tables.base_class import BasePublic

if TYPE_CHECKING:
    from instorage.database.tables.ai_models_table import CompletionModels, EmbeddingModels


class SecurityLevels(BasePublic):
    """Table for storing security levels."""

    # Core fields
    name: Mapped[str] = mapped_column(unique=True)
    description: Mapped[Optional[str]] = mapped_column()
    value: Mapped[int] = mapped_column()

    # Relationships
    completion_models: Mapped[list["CompletionModels"]] = relationship(
        back_populates="security_level",
        order_by="CompletionModels.created_at"
    )
    embedding_models: Mapped[list["EmbeddingModels"]] = relationship(
        back_populates="security_level",
        order_by="EmbeddingModels.created_at"
    )
