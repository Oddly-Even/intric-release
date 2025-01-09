# Copyright (c) 2024 Sundsvalls Kommun
#
# Licensed under the MIT License.

from uuid import UUID

from fastapi import APIRouter, Depends

from instorage.securitylevels.security_level_factory import get_security_level_service
from instorage.securitylevels.security_level_service import SecurityLevelService
from instorage.server import protocol
from instorage.server.protocol import responses
from instorage.securitylevels.api.security_level_models import (
    CreateSecurityLevelRequest,
    SecurityLevelPublic,
    UpdateSecurityLevelRequest,
)

router = APIRouter(prefix="/security-levels", tags=["Security Levels"])


@router.post(
    "", 
    response_model=SecurityLevelPublic, 
    status_code=201,
    responses=responses.get_responses([400, 409]),
)
async def create_security_level(
    request: CreateSecurityLevelRequest,
    service: SecurityLevelService = Depends(get_security_level_service),
) -> SecurityLevelPublic:
    """Create a new security level.
    
    Args:
        request: The security level creation request.
        
    Returns:
        The created security level.
        
    Raises:
        400: If the request is invalid.
        409: If a security level with the same name already exists.
    """
    security_level = await service.create_security_level(
        name=request.name,
        description=request.description,
        value=request.value,
    )
    return SecurityLevelPublic.model_validate(security_level)


@router.get(
    "", 
    response_model=list[SecurityLevelPublic],
    responses=responses.get_responses([403]),
)
async def list_security_levels(
    service: SecurityLevelService = Depends(get_security_level_service),
) -> list[SecurityLevelPublic]:
    """List all security levels ordered by value.
    
    Returns:
        List of security levels ordered by value.
        
    Raises:
        403: If the user doesn't have permission to list security levels.
    """
    security_levels = await service.list_security_levels()
    return [SecurityLevelPublic.model_validate(sl) for sl in security_levels]


@router.get(
    "/{id}", 
    response_model=SecurityLevelPublic,
    responses=responses.get_responses([403, 404]),
)
async def get_security_level(
    id: UUID,
    service: SecurityLevelService = Depends(get_security_level_service),
) -> SecurityLevelPublic:
    """Get a security level by ID.
    
    Args:
        id: The ID of the security level.
        
    Returns:
        The security level.
        
    Raises:
        403: If the user doesn't have permission to view the security level.
        404: If the security level doesn't exist.
    """
    security_level = await service.get_security_level(id)
    return SecurityLevelPublic.model_validate(security_level)


@router.patch(
    "/{id}", 
    response_model=SecurityLevelPublic,
    responses=responses.get_responses([400, 403, 404, 409]),
)
async def update_security_level(
    id: UUID,
    request: UpdateSecurityLevelRequest,
    service: SecurityLevelService = Depends(get_security_level_service),
) -> SecurityLevelPublic:
    """Update a security level.
    
    Args:
        id: The ID of the security level to update.
        request: The update request.
        
    Returns:
        The updated security level.
        
    Raises:
        400: If the request is invalid.
        403: If the user doesn't have permission to update the security level.
        404: If the security level doesn't exist.
        409: If updating the name would create a duplicate.
    """
    security_level = await service.update_security_level(
        id=id,
        name=request.name,
        description=request.description,
        value=request.value,
    )
    return SecurityLevelPublic.model_validate(security_level)


@router.delete(
    "/{id}", 
    status_code=204,
    responses=responses.get_responses([403, 404, 409]),
)
async def delete_security_level(
    id: UUID,
    service: SecurityLevelService = Depends(get_security_level_service),
) -> None:
    """Delete a security level.
    
    Args:
        id: The ID of the security level to delete.
        
    Raises:
        403: If the user doesn't have permission to delete the security level.
        404: If the security level doesn't exist.
        409: If the security level is in use by any spaces or models.
    """
    await service.delete_security_level(id) 