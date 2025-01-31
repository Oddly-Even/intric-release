# Copyright (c) 2024 Sundsvalls Kommun
#
# Licensed under the MIT License.

import json
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from instorage.assistants.api.assistant_models import AssistantPublic
from instorage.main.container.container import Container
from instorage.main.models import ModelId, PaginatedResponse
from instorage.server import protocol
from instorage.server.dependencies.container import get_container
from instorage.server.protocol import responses
from instorage.spaces.api.space_models import (
    AddSpaceMemberRequest,
    Applications,
    CreateSpaceAssistantRequest,
    CreateSpaceGroupsRequest,
    CreateSpaceGroupsResponse,
    CreateSpaceRequest,
    CreateSpaceServiceRequest,
    CreateSpaceServiceResponse,
    CreateSpaceWebsitesRequest,
    CreateSpaceWebsitesResponse,
    Knowledge,
    SpaceMember,
    SpacePublic,
    SpaceSparse,
    UpdateSpaceMemberRequest,
    UpdateSpaceRequest,
    SpaceUpdateDryRunRequest,
    SpaceUpdateDryRunResponse,
)

router = APIRouter()


@router.post("/", response_model=SpacePublic, status_code=201)
async def create_space(
    create_space_req: CreateSpaceRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.space_service()
    assembler = container.space_assembler()

    space = await service.create_space(name=create_space_req.name)

    return assembler.from_space_to_model(space)


@router.get(
    "/{id}/",
    response_model=SpacePublic,
    status_code=200,
    responses=responses.get_responses([404]),
)
async def get_space(
    id: UUID,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.space_service()
    assembler = container.space_assembler()

    space = await service.get_space(id)

    return assembler.from_space_to_model(space)


@router.patch(
    "/{id}/",
    response_model=SpacePublic,
    status_code=200,
    responses=responses.get_responses([400, 403, 404]),
)
async def update_space(
    id: UUID,
    update_space_req: UpdateSpaceRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    """Update a space with impact analysis for security level changes."""
    service = container.space_service()
    assembler = container.space_assembler()

    # Get current space to check current security level
    space = await service.get_space(id)

    # Analyze impact if security level is changing
    if update_space_req.security_level_id:
        orchestrator = container.security_level_orchestrator()
        security_level_service = container.security_level_service()
        
        # Get current and new security levels
        current_security_level = space.security_level
        new_security_level = await security_level_service.get_security_level(
            update_space_req.security_level_id
        ) if update_space_req.security_level_id else None

        # Analyze the impact
        analysis = await orchestrator.analyze_space_security_level_change(
            space_id=id,
            current_security_level=current_security_level,
            new_security_level=new_security_level,
        )
        # TODO

    def _get_model_ids_or_none(models: list[ModelId] | None):
        if models is None:
            return None
        return [model.id for model in models]

    space = await service.update_space(
        id=id,
        name=update_space_req.name,
        description=update_space_req.description,
        embedding_model_ids=_get_model_ids_or_none(update_space_req.embedding_models),
        completion_model_ids=_get_model_ids_or_none(update_space_req.completion_models),
        security_level_id=update_space_req.security_level_id,
    )

    return assembler.from_space_to_model(space)


@router.delete(
    "/{id}/",
    status_code=204,
    responses=responses.get_responses([403, 404]),
)
async def delete_space(
    id: UUID,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.space_service()

    await service.delete_space(id=id)


@router.get(
    "/",
    response_model=PaginatedResponse[SpaceSparse],
    status_code=200,
)
async def get_spaces(
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.space_service()
    assembler = container.space_assembler()

    spaces = await service.get_spaces()
    spaces = [assembler.from_space_to_model(space) for space in spaces]

    return protocol.to_paginated_response(spaces)


@router.get(
    "/{id}/applications/",
    response_model=Applications,
    responses=responses.get_responses([404]),
)
async def get_space_applications(
    id: UUID, container: Container = Depends(get_container(with_user=True))
):
    service = container.space_service()
    assembler = container.space_assembler()

    space = await service.get_space(id)

    return assembler.from_space_to_model(space).applications


@router.post(
    "/{id}/applications/assistants/",
    response_model=AssistantPublic,
    status_code=201,
    responses=responses.get_responses([400, 403, 404]),
)
async def create_space_assistant(
    id: UUID,
    assistant_in: CreateSpaceAssistantRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.assistant_service()
    assembler = container.space_assembler()

    assistant = await service.create_space_assistant(
        name=assistant_in.name, space_id=id
    )

    return assembler.from_assistant_to_model(assistant)


@router.post(
    "/{id}/applications/services/",
    response_model=CreateSpaceServiceResponse,
    status_code=201,
    responses=responses.get_responses([400, 403, 404]),
)
async def create_space_services(
    id: UUID,
    service_in: CreateSpaceServiceRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.service_service()
    assembler = container.space_assembler()

    assistant = await service.create_space_service(name=service_in.name, space_id=id)

    return assembler.from_service_to_model(assistant)


@router.get(
    "/{id}/knowledge/",
    response_model=Knowledge,
    responses=responses.get_responses([404]),
)
async def get_space_knowledge(
    id: UUID, container: Container = Depends(get_container(with_user=True))
):
    service = container.space_service()
    assembler = container.space_assembler()

    space = await service.get_space(id)

    return assembler.from_space_to_model(space).knowledge


@router.post(
    "/{id}/knowledge/groups/",
    response_model=CreateSpaceGroupsResponse,
    status_code=201,
    responses=responses.get_responses([400, 403, 404]),
)
async def create_space_groups(
    id: UUID,
    group: CreateSpaceGroupsRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.group_service()
    assembler = container.space_assembler()

    embedding_model_id = group.embedding_model.id if group.embedding_model else None

    group = await service.create_space_group(
        name=group.name, space_id=id, embedding_model_id=embedding_model_id
    )

    return assembler.from_group_to_model(group)


@router.post(
    "/{id}/knowledge/websites/",
    response_model=CreateSpaceWebsitesResponse,
    status_code=201,
    responses=responses.get_responses([400, 403, 404]),
)
async def create_space_websites(
    id: UUID,
    website: CreateSpaceWebsitesRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.website_service()
    assembler = container.space_assembler()

    embedding_model_id = website.embedding_model.id if website.embedding_model else None

    website = await service.create_space_website(
        space_id=id,
        name=website.name,
        url=website.url,
        download_files=website.download_files,
        crawl_type=website.crawl_type,
        update_interval=website.update_interval,
        embedding_model_id=embedding_model_id,
    )

    return assembler.from_website_to_model(website)


@router.post(
    "/{id}/members/",
    response_model=SpaceMember,
    responses=responses.get_responses([403, 404]),
)
async def add_space_member(
    id: UUID,
    add_space_member_req: AddSpaceMemberRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.space_service()

    return await service.add_member(
        id, member_id=add_space_member_req.id, role=add_space_member_req.role
    )


@router.patch(
    "/{id}/members/{user_id}/",
    response_model=SpaceMember,
    responses=responses.get_responses([403, 404, 400]),
)
async def change_role_of_member(
    id: UUID,
    user_id: UUID,
    update_space_member_req: UpdateSpaceMemberRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.space_service()

    return await service.change_role_of_member(
        id, user_id, update_space_member_req.role
    )


@router.delete(
    "/{id}/members/{user_id}/",
    status_code=204,
    responses=responses.get_responses([403, 404, 400]),
)
async def remove_space_member(
    id: UUID,
    user_id: UUID,
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.space_service()

    await service.remove_member(id, user_id)


@router.get("/type/personal/", response_model=SpacePublic)
async def get_personal_space(
    container: Container = Depends(get_container(with_user=True)),
):
    service = container.space_service()
    assembler = container.space_assembler()

    space = await service.get_personal_space()

    return assembler.from_space_to_model(space)


@router.post(
    "/{id}/update/dryrun/",
    response_model=SpaceUpdateDryRunResponse,
    responses=responses.get_responses([404]),
)
async def update_space_dryrun(
    id: UUID,
    dryrun_request: SpaceUpdateDryRunRequest,
    container: Container = Depends(get_container(with_user=True)),
):
    """
    Analyze the impact of updating a space's properties without actually applying the changes.
    Currently supports:
    - Security level changes: Shows which models would be affected
    """
    service = container.space_service()
    assembler = container.space_assembler()

    # Get current space to check current security level
    space = await service.get_space(id)

    # Analyze security level changes
    if dryrun_request.security_level_id:
        orchestrator = container.security_level_orchestrator()
        security_level_service = container.security_level_service()
        
        # Get current and new security levels
        current_security_level = space.security_level
        new_security_level = await security_level_service.get_security_level(
            dryrun_request.security_level_id
        ) if dryrun_request.security_level_id else None

        # Analyze the impact
        analysis = await orchestrator.analyze_space_security_level_change(
            space_id=id,
            current_security_level=current_security_level,
            new_security_level=new_security_level,
        )
        
        return SpaceUpdateDryRunResponse(
            unavailable_completion_models=analysis.unavailable_completion_models,
            unavailable_embedding_models=analysis.unavailable_embedding_models,
            warning=analysis.warning,
        )

    return SpaceUpdateDryRunResponse(
        unavailable_completion_models=[],
        unavailable_embedding_models=[],
    )
