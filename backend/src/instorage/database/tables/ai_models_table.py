from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from instorage.database.tables.base_class import BaseCrossReference, BasePublic
from instorage.database.tables.tenant_table import Tenants
from instorage.database.tables.security_levels_table import SecurityLevels


class CompletionModels(BasePublic):
    name: Mapped[str] = mapped_column(unique=True)
    nickname: Mapped[str] = mapped_column()
    open_source: Mapped[Optional[bool]] = mapped_column()
    token_limit: Mapped[int] = mapped_column()
    is_deprecated: Mapped[bool] = mapped_column(server_default="False")
    nr_billion_parameters: Mapped[Optional[int]] = mapped_column()
    hf_link: Mapped[Optional[str]] = mapped_column()

    family: Mapped[str] = mapped_column()
    stability: Mapped[str] = mapped_column()
    hosting: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    deployment_name: Mapped[Optional[str]] = mapped_column()
    org: Mapped[Optional[str]] = mapped_column()
    vision: Mapped[bool] = mapped_column(server_default="False")


class CompletionModelSettings(BaseCrossReference):
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(Tenants.id, ondelete="CASCADE"), primary_key=True
    )
    completion_model_id: Mapped[UUID] = mapped_column(
        ForeignKey(CompletionModels.id, ondelete="CASCADE"), primary_key=True
    )
    is_org_enabled: Mapped[bool] = mapped_column(server_default="False")

    # Security level relationship
    security_level_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey(SecurityLevels.id, ondelete="SET NULL"),
        nullable=True
    )
    security_level: Mapped[Optional["SecurityLevels"]] = relationship(
        back_populates="completion_model_settings"
    )


class EmbeddingModels(BasePublic):
    name: Mapped[str] = mapped_column(unique=True)
    open_source: Mapped[bool] = mapped_column()
    dimensions: Mapped[Optional[int]] = mapped_column()
    max_input: Mapped[Optional[int]] = mapped_column()
    is_deprecated: Mapped[bool] = mapped_column(server_default="False")
    hf_link: Mapped[Optional[str]] = mapped_column()

    family: Mapped[str] = mapped_column()
    stability: Mapped[str] = mapped_column()
    hosting: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column()
    org: Mapped[Optional[str]] = mapped_column()


class EmbeddingModelSettings(BaseCrossReference):
    tenant_id: Mapped[UUID] = mapped_column(
        ForeignKey(Tenants.id, ondelete="CASCADE"), primary_key=True
    )
    embedding_model_id: Mapped[UUID] = mapped_column(
        ForeignKey(EmbeddingModels.id, ondelete="CASCADE"), primary_key=True
    )
    is_org_enabled: Mapped[bool] = mapped_column(server_default="False")

    # Security level relationship
    security_level_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey(SecurityLevels.id, ondelete="SET NULL"),
        nullable=True
    )
    security_level: Mapped[Optional["SecurityLevels"]] = relationship(
        back_populates="embedding_model_settings"
    )
