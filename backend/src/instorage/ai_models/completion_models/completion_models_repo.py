# Copyright (c) 2024 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

from instorage.ai_models.completion_models.completion_model import (
    CompletionModel,
    CompletionModelCreate,
    CompletionModelUpdate,
)
from instorage.database.database import AsyncSession
from instorage.database.repositories.base import BaseRepositoryDelegate
from instorage.database.tables.ai_models_table import (
    CompletionModels,
    CompletionModelSettings,
)
from instorage.main.exceptions import UniqueException
from instorage.main.models import IdAndName


class CompletionModelsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.delegate = BaseRepositoryDelegate(
            session, CompletionModels, CompletionModel
        )

    async def _get_model_settings(
        self, id: UUID, tenant_id: UUID
    ) -> CompletionModelSettings | None:
        query = sa.select(CompletionModelSettings).where(
            CompletionModelSettings.tenant_id == tenant_id,
            CompletionModelSettings.completion_model_id == id,
        )
        return await self.session.scalar(query)

    async def _get_models_settings_mapper(
        self, tenant_id: UUID
    ) -> dict[UUID, CompletionModelSettings]:
        query = sa.select(CompletionModelSettings).where(
            CompletionModelSettings.tenant_id == tenant_id
        )
        settings = await self.session.scalars(query)
        return {s.completion_model_id: s for s in settings}

    async def get_model(self, id: UUID, tenant_id: UUID) -> CompletionModel:
        model = await self.delegate.get(id)

        settings = await self._get_model_settings(id, tenant_id)
        if settings:
            model.is_org_enabled = settings.is_org_enabled
            model.security_level_id = settings.security_level_id
        return model

    async def get_model_by_name(self, name: str) -> CompletionModel:
        return await self.delegate.get_by(conditions={CompletionModels.name: name})

    async def create_model(self, model: CompletionModelCreate) -> CompletionModel:
        return await self.delegate.add(model)

    async def enable_completion_model(
        self,
        is_org_enabled: bool,
        completion_model_id: UUID,
        security_level_id: UUID | None,
        tenant_id: UUID,
    ):
        query = sa.select(CompletionModelSettings).where(
            CompletionModelSettings.tenant_id == tenant_id,
            CompletionModelSettings.completion_model_id == completion_model_id,
        )
        settings = await self.session.scalar(query)

        try:
            if settings:
                query = (
                    sa.update(CompletionModelSettings)
                    .values(
                        is_org_enabled=is_org_enabled,
                        security_level_id=security_level_id,
                    )
                    .where(
                        CompletionModelSettings.tenant_id == tenant_id,
                        CompletionModelSettings.completion_model_id
                        == completion_model_id,
                    )
                    .returning(CompletionModelSettings)
                )
                return await self.session.scalar(query)
            query = (
                sa.insert(CompletionModelSettings)
                .values(
                    is_org_enabled=is_org_enabled,
                    security_level_id=security_level_id,
                    completion_model_id=completion_model_id,
                    tenant_id=tenant_id,
                )
                .returning(CompletionModelSettings)
            )
            return await self.session.scalar(query)
        except IntegrityError as e:
            raise UniqueException("Default completion model already exists.") from e

    async def set_completion_model_security_level(
        self,
        completion_model_id: UUID,
        security_level_id: Optional[UUID],
        tenant_id: UUID,
    ) -> CompletionModelSettings:
        """Set the security level for a completion model.

        Args:
            completion_model_id: The ID of the completion model.
            security_level_id: The ID of the security level. If None, the security level is unset.
            tenant_id: The ID of the tenant.

        Returns:
            The updated completion model settings.
        """
        query = (
            sa.update(CompletionModelSettings)
            .values(security_level_id=security_level_id)
            .where(
                CompletionModelSettings.tenant_id == tenant_id,
                CompletionModelSettings.completion_model_id == completion_model_id,
            )
            .returning(CompletionModelSettings)
        )
        res = await self.session.scalar(query)
        if not res:
            raise ValueError("Completion model settings not found (is it enabled?)")
        return res

    async def update_model(self, model: CompletionModelUpdate) -> CompletionModel:
        return await self.delegate.update(model)

    async def delete_model(self, id: UUID) -> CompletionModel:
        stmt = (
            sa.delete(CompletionModels)
            .where(CompletionModels.id == id)
            .returning(CompletionModels)
        )

        await self.delegate.get_record_from_query(stmt)

    async def get_models(
        self,
        tenant_id: UUID = None,
        is_deprecated: bool = False,
        id_list: list[UUID] = None,
    ) -> list[CompletionModel]:
        query = (
            sa.select(CompletionModels)
            .where(CompletionModels.is_deprecated == is_deprecated)
            .order_by(CompletionModels.created_at)
        )

        if id_list is not None:
            query = query.where(CompletionModels.id.in_(id_list))

        models: list[CompletionModel] = await self.delegate.get_models_from_query(query)

        if tenant_id is not None:
            settings_mapper = await self._get_models_settings_mapper(tenant_id)

            for model in models:
                model_settings = settings_mapper.get(model.id, None)
                model.is_org_enabled = (
                    model_settings.is_org_enabled if model_settings else False
                )
                model.security_level_id = (
                    model_settings.security_level_id if model_settings else None
                )
        return models

    async def get_ids_and_names(self) -> list[(UUID, str)]:
        stmt = sa.select(CompletionModels)

        models = await self.delegate.get_records_from_query(stmt)

        return [IdAndName(id=model.id, name=model.name) for model in models.all()]
