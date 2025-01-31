# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import Optional, List
from uuid import UUID
from dataclasses import dataclass

from instorage.main.exceptions import BadRequestException, NotFoundException
from instorage.securitylevels.security_level import SecurityLevel
from instorage.securitylevels.security_level_service import SecurityLevelService
from instorage.ai_models.completion_models.completion_model import (
    CompletionModelPublic,
)
from instorage.ai_models.embedding_models.embedding_model import (
    EmbeddingModelPublic,
)
from instorage.ai_models.completion_models.completion_models_repo import (
    CompletionModelsRepository,
)
from instorage.ai_models.embedding_models.embedding_models_repo import (
    EmbeddingModelsRepository,
)
from instorage.spaces.space_repo import SpaceRepository
from instorage.spaces.space import Space
from instorage.users.user import UserInDB
from instorage.securitylevels.security_level_analysis import (
    SecurityLevelAnalysis,
    analyze_space_model_changes,
    generate_warning_message,
)


@dataclass
class AffectedSpace:
    space_id: UUID
    old_completion_models: List[CompletionModelPublic]
    old_embedding_models: List[EmbeddingModelPublic]
    new_completion_models: List[CompletionModelPublic]
    new_embedding_models: List[EmbeddingModelPublic]

    @property
    def removed_completion_models(self) -> List[CompletionModelPublic]:
        return [
            m for m in self.old_completion_models if m not in self.new_completion_models
        ]

    @property
    def removed_embedding_models(self) -> List[EmbeddingModelPublic]:
        return [
            m for m in self.old_embedding_models if m not in self.new_embedding_models
        ]

    @property
    def added_completion_models(self) -> List[CompletionModelPublic]:
        return [
            m for m in self.new_completion_models if m not in self.old_completion_models
        ]

    @property
    def added_embedding_models(self) -> List[EmbeddingModelPublic]:
        return [
            m for m in self.new_embedding_models if m not in self.old_embedding_models
        ]

    def did_change(self) -> bool:
        return (
            self.removed_completion_models
            or self.removed_embedding_models
            or self.added_completion_models
            or self.added_embedding_models
        )


@dataclass
class SecurityLevelChangeAnalysis:
    """Analysis of the impact of changing security levels."""

    current_security_level: Optional[SecurityLevel]
    new_security_level: Optional[SecurityLevel]
    affected_spaces: List[AffectedSpace]


@dataclass
class SecurityLevelResponse:
    """Response type for security level operations that may include warnings."""

    security_level: SecurityLevel
    warning: Optional[str] = None


@dataclass
class SpaceSecurityAnalysisResponse:
    """Response type for space security level analysis."""

    analysis: SecurityLevelAnalysis
    warning: Optional[str] = None


@dataclass
class SpaceSecurityLevelChangeAnalysis:
    """Analysis of the impact of changing a space's security level."""

    space: Space
    new_security_level: Optional[SecurityLevel]
    available_completion_models: List[CompletionModelPublic]
    available_embedding_models: List[EmbeddingModelPublic]


class SecurityLevelOrchestrator:
    """
    Orchestrates security level operations by coordinating between services.
    Handles analysis and validation of security level changes across the system.
    """

    def __init__(
        self,
        user: UserInDB,
        security_level_service: SecurityLevelService,
        completion_model_repo: CompletionModelsRepository,
        embedding_model_repo: EmbeddingModelsRepository,
        space_repo: SpaceRepository,
    ):
        self.user = user
        self.security_level_service = security_level_service
        self.completion_model_repo = completion_model_repo
        self.embedding_model_repo = embedding_model_repo
        self.space_repo = space_repo

    async def _analyze_space_models_for_security_level(
        self,
        space: Space,
        new_security_level: Optional[SecurityLevel],
    ) -> SpaceSecurityLevelChangeAnalysis:
        available_completion_models: List[CompletionModelPublic] = []
        available_embedding_models: List[EmbeddingModelPublic] = []

        for model in space.completion_models:
            if new_security_level:
                if not model.security_level:
                    continue
                if model.security_level.value >= new_security_level.value:
                    available_completion_models.append(model)
            else:
                if not model.security_level:
                    available_completion_models.append(model)

        for model in space.embedding_models:
            if new_security_level:
                if not model.security_level:
                    continue
                if model.security_level.value >= new_security_level.value:
                    available_embedding_models.append(model)
            else:
                if not model.security_level:
                    available_embedding_models.append(model)

        return SpaceSecurityLevelChangeAnalysis(
            space=space,
            new_security_level=new_security_level,
            available_completion_models=available_completion_models,
            available_embedding_models=available_embedding_models,
        )

    async def _analyze_security_level_change(
        self,
        current_security_level: Optional[SecurityLevel],
        new_security_level: Optional[SecurityLevel],
        space_id: Optional[UUID],
    ) -> SecurityLevelAnalysis:
        """Analyze the impact of changing security levels."""
        affected_spaces = []

        if space_id:
            # Analyzing single space
            space = await self.space_repo.get(space_id)
            if not space:
                return SecurityLevelAnalysis(affected_spaces=[])

            space_analysis = analyze_space_model_changes(
                space=space,
                current_security_level=current_security_level,
                new_security_level=new_security_level,
            )

            if space_analysis.has_changes:
                affected_spaces.append(space_analysis)
        else:
            # Analyzing all spaces that could be affected
            if current_security_level:
                spaces = await self.space_repo.get_spaces_by_security_level(
                    current_security_level.id
                )
            else:
                spaces = []  # No spaces affected when there's no current security level

            for space in spaces:
                space_analysis = analyze_space_model_changes(
                    space=space,
                    current_security_level=current_security_level,
                    new_security_level=new_security_level,
                )

                if space_analysis.has_changes:
                    affected_spaces.append(space_analysis)

        has_changes = any(space.has_changes for space in affected_spaces)
        total_affected_spaces = len([space for space in affected_spaces if space.has_changes])
        
        return SecurityLevelAnalysis(
            has_changes=has_changes,
            total_affected_spaces=total_affected_spaces,
            space_analyses=affected_spaces,
        )

    async def analyze_space_security_level_change(
        self,
        space_id: UUID,
        security_level_id: Optional[UUID],
    ) -> SpaceSecurityAnalysisResponse:
        """
        Analyze the impact of changing a space's security level.
        This is used when updating a space's security level to understand the impact
        on the space's models.
        """
        # Get the space
        space = await self.space_repo.get(space_id)
        if not space:
            raise NotFoundException("Space not found")

        # Get the new security level if one is specified
        new_security_level: Optional[SecurityLevel] = None
        if security_level_id is not None:
            new_security_level = await self.security_level_service.get_security_level(
                security_level_id
            )

        analysis = await self._analyze_security_level_change(
            current_security_level=space.security_level,
            new_security_level=new_security_level,
            space_id=space_id,
        )

        return SpaceSecurityAnalysisResponse(
            analysis=analysis,
            warning=generate_warning_message(analysis) if analysis.has_changes else None,
        )

    async def create_security_level(
        self, name: str, description: Optional[str], value: int
    ) -> SecurityLevelResponse:
        """Create a new security level with impact analysis."""
        # First create the security level
        created = await self.security_level_service.create_security_level(
            name=name,
            description=description,
            value=value,
        )

        # Analyze impact after creation
        analysis = await self._analyze_security_level_change(
            current_security_level=None,
            new_security_level=created,
            space_id=None,  # Analyze all spaces
        )

        warning = None
        if analysis.has_changes:
            warning = f"Creating this security level will affect {analysis.total_affected_spaces} spaces"
            if analysis.total_affected_spaces > 0:
                warning += " and may make some models unavailable"

        return SecurityLevelResponse(
            security_level=created,
            warning=warning,
        )

    async def update_security_level(
        self,
        id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None,
        value: Optional[int] = None,
    ) -> SecurityLevelResponse:
        """Update a security level with impact analysis."""
        # Get current security level
        current = await self.security_level_service.get_security_level(id)

        # Analyze impact before update if value is changing
        warning = None
        if value is not None and value != current.value:
            analysis = await self._analyze_security_level_change(
                current_security_level=current,
                new_security_level=SecurityLevel(
                    id=current.id,
                    tenant_id=current.tenant_id,
                    name=current.name,
                    description=current.description,
                    value=value,
                    created_at=current.created_at,
                    updated_at=current.updated_at,
                ),
                space_id=None,  # Analyze all spaces
            )
            if analysis.has_changes:
                warning = f"Updating this security level will affect {analysis.total_affected_spaces} spaces"
                if analysis.total_affected_spaces > 0:
                    warning += " and may make some models unavailable"

        # Perform the update
        updated = await self.security_level_service.update_security_level(
            id=id,
            name=name,
            description=description,
            value=value,
        )

        return SecurityLevelResponse(
            security_level=updated,
            warning=warning,
        )

    async def delete_security_level(self, id: UUID) -> SecurityLevelAnalysis:
        """Delete a security level with impact analysis."""
        # Get current security level
        current = await self.security_level_service.get_security_level(id)

        # Analyze impact before deletion
        analysis = await self._analyze_security_level_change(
            current_security_level=current,
            new_security_level=None,
            space_id=None,  # Analyze all spaces
        )

        if analysis.has_changes:
            # Don't delete if there are affected spaces
            return analysis

        # Perform the deletion
        await self.security_level_service.delete_security_level(id)
        return analysis

    async def analyze_security_level_update(
        self,
        id: UUID,
        value: Optional[int] = None,
    ) -> SecurityLevelAnalysis:
        """
        Analyze the impact of updating a security level's properties without applying changes.
        Currently supports:
        - Value changes: Shows which spaces and models would be affected
        """
        security_level = await self.security_level_service.get_security_level(id)
        if value is None:
            value = security_level.value

        new_security_level = SecurityLevel(
            id=security_level.id,
            tenant_id=security_level.tenant_id,
            name=security_level.name,
            description=security_level.description,
            value=value,
            created_at=security_level.created_at,
            updated_at=security_level.updated_at,
        )

        return await self._analyze_security_level_change(
            current_security_level=security_level,
            new_security_level=new_security_level,
            space_id=None,  # Analyze all spaces
        )

    async def update_space_security_level(
        self,
        space_id: UUID,
        security_level_id: Optional[UUID],
    ) -> Space:
        """
        Update a space's security level and handle all related model filtering.
        This is the only way to change a space's security level.

        Args:
            space_id: The ID of the space to update
            security_level_id: The new security level ID, or None to remove security level

        Returns:
            The updated space

        Raises:
            NotFoundException: If the space is not found
        """
        # Get the space
        space = await self.space_repo.get(space_id)
        if not space:
            raise NotFoundException("Space not found")

        # If security level is not changing, return early
        if security_level_id is None and not space.security_level:
            return space
        if space.security_level and security_level_id == space.security_level.id:
            return space

        # Get the new security level if one is specified
        new_security_level: Optional[SecurityLevel] = None
        if security_level_id is not None:
            new_security_level = await self.security_level_service.get_security_level(
                security_level_id
            )

        # Analyze impact
        analysis = await self._analyze_security_level_change(
            current_security_level=space.security_level,
            new_security_level=new_security_level,
            space_id=space_id,
        )

        # Get the space analysis (should be the only one)
        space_analysis = analysis.space_analyses[0] if analysis.space_analyses else None

        # Initialize available models with current models
        available_completion_models = list(space.completion_models)
        available_embedding_models = list(space.embedding_models)

        # If space is affected, filter models based on analysis
        if space_analysis and space_analysis.has_changes:
            # Filter out models that will become unavailable
            available_completion_models = [
                model for model in space.completion_models
                if not (
                    space_analysis.completion_model_change and
                    space_analysis.completion_model_change.model_id == model.id and
                    not space_analysis.completion_model_change.is_available
                )
            ]
            available_embedding_models = [
                model for model in space.embedding_models
                if not (
                    space_analysis.embedding_model_change and
                    space_analysis.embedding_model_change.model_id == model.id and
                    not space_analysis.embedding_model_change.is_available
                )
            ]

        # Update the space with the new security level and filtered models
        space.update(
            security_level=new_security_level,
            completion_models=available_completion_models,
            embedding_models=available_embedding_models,
        )

        return await self.space_repo.update(space)

    async def update_completion_model_security_level(
        self,
        completion_model_id: UUID,
        security_level_id: Optional[UUID],
    ) -> CompletionModelPublic:
        """
        Update a completion model's security level with impact analysis.
        This is the only way to change a completion model's security level.

        Args:
            completion_model_id: The ID of the completion model to update
            security_level_id: The new security level ID, or None to remove security level

        Returns:
            The updated completion model

        Raises:
            NotFoundException: If the completion model is not found
            BadRequestException: If the security level change would cause issues
        """
        # Get the current model
        model = await self.completion_model_repo.get_model(
            completion_model_id, tenant_id=self.user.tenant_id
        )
        if not model:
            raise NotFoundException("Completion model not found")

        # If security level is not changing, return early
        if security_level_id is None and model.security_level_id is None:
            return model
        if security_level_id == model.security_level_id:
            return model

        # Get the new security level if one is specified
        new_security_level: Optional[SecurityLevel] = None
        if security_level_id is not None:
            new_security_level = await self.security_level_service.get_security_level(
                security_level_id
            )

        # Get all spaces that use this model
        spaces = await self.space_repo.get_spaces_by_completion_model(completion_model_id)

        # Analyze impact for each space
        affected_spaces = []
        for space in spaces:
            analysis = await self._analyze_security_level_change(
                current_security_level=space.security_level,
                new_security_level=space.security_level,  # Space's security level isn't changing
                space_id=space.id,
            )
            if analysis.has_changes:
                affected_spaces.extend(analysis.space_analyses)

        # If there are affected spaces, raise an error
        if affected_spaces:
            raise BadRequestException(
                f"Cannot update security level as it would affect {len(affected_spaces)} spaces"
            )

        # Apply the change through the repository
        await self.completion_model_repo.set_completion_model_security_level(
            completion_model_id=completion_model_id,
            security_level_id=security_level_id,
            tenant_id=self.user.tenant_id,
        )

        # Get and return the updated model
        updated_model = await self.completion_model_repo.get_model(
            completion_model_id, tenant_id=self.user.tenant_id
        )
        return CompletionModelPublic(
            **updated_model.model_dump(),
            is_locked=False,  # These will be set by the service layer
            can_access=True,  # These will be set by the service layer
        )
