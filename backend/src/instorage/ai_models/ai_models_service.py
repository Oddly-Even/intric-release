from typing import Optional
from uuid import UUID

from instorage.ai_models.completion_models.completion_model import (
    CompletionModel,
    CompletionModelFamily,
    CompletionModelPublic,
    CompletionModelUpdateFlags,
    CompletionModelSecurityLevelUpdate,
    ModelHostingLocation,
)
from instorage.ai_models.completion_models.completion_models_repo import (
    CompletionModelsRepository,
)
from instorage.ai_models.embedding_models.embedding_model import (
    EmbeddingModel,
    EmbeddingModelPublic,
    EmbeddingModelUpdateFlags,
    EmbeddingModelSecurityLevelUpdate,
)
from instorage.ai_models.embedding_models.embedding_models_repo import (
    EmbeddingModelsRepository,
)
from instorage.securitylevels.security_level_service import SecurityLevelService
from instorage.main.config import get_settings
from instorage.main.exceptions import (
    BadRequestException,
    NotFoundException,
    UnauthorizedException,
)
from instorage.modules.module import Modules
from instorage.roles.permissions import Permission, validate_permissions
from instorage.tenants.tenant_repo import TenantRepository
from instorage.users.user import UserInDB

class AIModelsService:
    def __init__(
        self,
        user: UserInDB,
        embedding_model_repo: EmbeddingModelsRepository,
        completion_model_repo: CompletionModelsRepository,
        security_level_service: SecurityLevelService,
        tenant_repo: TenantRepository,
    ):
        self.user = user
        self.embedding_model_repo = embedding_model_repo
        self.completion_model_repo = completion_model_repo
        self.tenant_repo = tenant_repo
        self.security_level_service = security_level_service

    def _is_locked(
        self,
        model: CompletionModel | EmbeddingModel,
    ):
        if model.hosting == ModelHostingLocation.EU:
            if Modules.EU_HOSTING not in self.user.modules:
                return True
        return False

    def _can_access(
        self,
        model: CompletionModel | EmbeddingModel,
    ):
        if (
            not self._is_locked(model)
            and not model.is_deprecated
            and model.is_org_enabled
        ):
            return True

        return False

    def _get_latest_available_model(
        self, models: list[CompletionModelPublic | EmbeddingModelPublic]
    ):
        sorted_models = sorted(models, key=lambda model: model.created_at, reverse=True)

        for model in sorted_models:
            if model.can_access:
                return model

    async def get_embedding_models(
        self, id_list: list[UUID] = None
    ) -> list[EmbeddingModelPublic]:
        embedding_models = await self.embedding_model_repo.get_models(
            tenant_id=self.user.tenant_id, is_deprecated=False, id_list=id_list
        )

        models = []
        for model in embedding_models:
            models.append(
                EmbeddingModelPublic(
                    **model.model_dump(),
                    is_locked=self._is_locked(model),
                    can_access=self._can_access(model),
                )
            )

        return models

    async def get_embedding_model(self, id: UUID, include_non_accessible: bool = False):
        model = await self.embedding_model_repo.get_model(
            id, tenant_id=self.user.tenant_id
        )

        print(f"ai_models_service embedding model: {model.id}")

        if model.is_deprecated:
            raise BadRequestException(
                f"EmbeddingModel {model.name} not supported anymore."
            )

        can_access = self._can_access(model)
        if not can_access and not include_non_accessible:
            raise UnauthorizedException(
                "Unauthorized. User has no permissions to access."
            )

        if not model.security_level_id:
            security_level = None
        else:
            security_level = await self.security_level_service.get_security_level(
                model.security_level_id
            )

        return EmbeddingModelPublic(
            **model.model_dump(),
            is_locked=self._is_locked(model),
            can_access=can_access,
            security_level=security_level,
        )

    async def get_latest_available_embedding_model(self):
        models = await self.get_embedding_models()

        return self._get_latest_available_model(models)

    async def get_completion_models(
        self, id_list: list[UUID] = None
    ) -> list[CompletionModelPublic]:
        completion_models = await self.completion_model_repo.get_models(
            tenant_id=self.user.tenant_id,
            is_deprecated=False,
            id_list=id_list,
        )

        models = []
        for model in completion_models:
            if (
                model.family == CompletionModelFamily.AZURE
                and not get_settings().using_azure_models
            ):
                continue

            models.append(
                CompletionModelPublic(
                    **model.model_dump(),
                    is_locked=self._is_locked(model),
                    can_access=self._can_access(model),
                )
            )

        return models

    async def get_completion_model(self, id: UUID, include_non_accessible: bool = False):
        model = await self.completion_model_repo.get_model(
            id, tenant_id=self.user.tenant_id
        )

        if (
            model.family == CompletionModelFamily.AZURE
            and not get_settings().using_azure_models
        ):
            raise NotFoundException()

        if model.is_deprecated:
            raise BadRequestException(
                f"CompletionModel {model.name} not supported anymore."
            )

        can_access = self._can_access(model)
        if not can_access and not include_non_accessible:
            raise UnauthorizedException(
                "Unauthorized. User has no permissions to access."
            )

        if not model.security_level_id:
            security_level = None
        else:
            security_level = await self.security_level_service.get_security_level(
                model.security_level_id
            )

        return CompletionModelPublic(
            **model.model_dump(),
            is_locked=self._is_locked(model),
            can_access=can_access,
            security_level=security_level,
        )

    async def get_latest_available_completion_model(self):
        models = await self.get_completion_models()

        return self._get_latest_available_model(models)

    @validate_permissions(Permission.ADMIN)
    async def enable_completion_model(
        self, completion_model_id: UUID, data: CompletionModelUpdateFlags
    ):
        await self.completion_model_repo.enable_completion_model(
            is_org_enabled=data.is_org_enabled,
            completion_model_id=completion_model_id,
            security_level_id=data.security_level_id,
            tenant_id=self.user.tenant_id,
        )

        model = await self.completion_model_repo.get_model(
            completion_model_id, tenant_id=self.user.tenant_id
        )
        return CompletionModelPublic(
            **model.model_dump(),
            is_locked=self._is_locked(model),
            can_access=self._can_access(model),
        )

    @validate_permissions(Permission.ADMIN)
    async def set_completion_model_security_level(
        self, completion_model_id: UUID, data: CompletionModelSecurityLevelUpdate
    ):
        return await self._set_completion_model_security_level(
            completion_model_id, data.security_level_id
        )

    @validate_permissions(Permission.ADMIN)
    async def unset_completion_model_security_level(
        self,
        completion_model_id: UUID,
    ):
        return await self._set_completion_model_security_level(
            completion_model_id, None
        )

    async def _set_completion_model_security_level(
        self, completion_model_id: UUID, security_level_id: Optional[UUID]
    ) -> CompletionModelPublic:
        await self.completion_model_repo.set_completion_model_security_level(
            completion_model_id=completion_model_id,
            security_level_id=security_level_id,
            tenant_id=self.user.tenant_id,
        )

        model = await self.completion_model_repo.get_model(
            completion_model_id, tenant_id=self.user.tenant_id
        )
        return CompletionModelPublic(
            **model.model_dump(),
            is_locked=self._is_locked(model),
            can_access=self._can_access(model),
        )

    @validate_permissions(Permission.ADMIN)
    async def enable_embedding_model(
        self, embedding_model_id: UUID, data: EmbeddingModelUpdateFlags
    ):
        await self.embedding_model_repo.enable_embedding_model(
            is_org_enabled=data.is_org_enabled,
            embedding_model_id=embedding_model_id,
            security_level_id=data.security_level_id,
            tenant_id=self.user.tenant_id,
        )

        model = await self.embedding_model_repo.get_model(
            embedding_model_id, tenant_id=self.user.tenant_id
        )
        return EmbeddingModelPublic(
            **model.model_dump(),
            is_locked=self._is_locked(model),
            can_access=self._can_access(model),
        )

    @validate_permissions(Permission.ADMIN)
    async def set_embedding_model_security_level(
        self, embedding_model_id: UUID, data: EmbeddingModelSecurityLevelUpdate
    ):
        return await self._set_embedding_model_security_level(
            embedding_model_id, data.security_level_id
        )

    @validate_permissions(Permission.ADMIN)
    async def unset_embedding_model_security_level(
        self,
        embedding_model_id: UUID,
    ):
        return await self._set_embedding_model_security_level(embedding_model_id, None)

    async def _set_embedding_model_security_level(
        self, embedding_model_id: UUID, security_level_id: Optional[UUID]
    ) -> EmbeddingModelPublic:
        await self.embedding_model_repo.set_embedding_model_security_level(
            embedding_model_id=embedding_model_id,
            security_level_id=security_level_id,
            tenant_id=self.user.tenant_id,
        )

        model = await self.embedding_model_repo.get_model(
            embedding_model_id, tenant_id=self.user.tenant_id
        )
        return EmbeddingModelPublic(
            **model.model_dump(),
            is_locked=self._is_locked(model),
            can_access=self._can_access(model),
        )
