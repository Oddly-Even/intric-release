# Copyright (c) 2024 Sundsvalls Kommun
#
# Licensed under the MIT License.

from uuid import UUID

from fastapi import APIRouter, Depends

from instorage.ai_models.ai_models_factory import get_ai_models_service
from instorage.ai_models.ai_models_service import AIModelsService
from instorage.ai_models.completion_models.completion_model import (
    CompletionModelPublic,
    CompletionModelUpdateFlags,
    CompletionModelSecurityLevelUpdate,
)
from instorage.main.models import PaginatedResponse
from instorage.server import protocol
from instorage.server.protocol import responses
from instorage.main.container.container import Container
from instorage.server.dependencies.container import get_container

router = APIRouter()


@router.get(
    "/",
    response_model=PaginatedResponse[CompletionModelPublic],
)
async def get_completion_models(
    service: AIModelsService = Depends(get_ai_models_service),
):
    models = await service.get_completion_models()

    return protocol.to_paginated_response(models)


@router.post(
    "/{id}/",
    response_model=CompletionModelPublic,
    responses=responses.get_responses([404]),
)
async def enable_completion_model(
    id: UUID,
    data: CompletionModelUpdateFlags,
    service: AIModelsService = Depends(get_ai_models_service),
):
    return await service.enable_completion_model(completion_model_id=id, data=data)


@router.put(
    "/{id}/security-level",
    response_model=CompletionModelPublic,
    responses=responses.get_responses([404]),
)
async def set_completion_model_security_level(
    id: UUID,
    data: CompletionModelSecurityLevelUpdate,
    container: Container = Depends(get_container(with_user=True)),
):
    """Set the security level for a completion model with impact analysis."""
    orchestrator = container.security_level_orchestrator()
    return await orchestrator.update_completion_model_security_level(
        completion_model_id=id,
        security_level_id=data.security_level_id,
    )


@router.delete(
    "/{id}/security-level",
    response_model=CompletionModelPublic,
)
async def unset_completion_model_security_level(
    id: UUID,
    container: Container = Depends(get_container(with_user=True)),
):
    """Remove the security level from a completion model with impact analysis."""
    orchestrator = container.security_level_orchestrator()
    return await orchestrator.update_completion_model_security_level(
        completion_model_id=id,
        security_level_id=None,
    )
