# Copyright (c) 2025 Sundsvalls Kommun
#
# Licensed under the MIT License.

from typing import Callable, Optional, TypeVar, Tuple, List, Set, Protocol, TypeAlias
from uuid import UUID
from dataclasses import dataclass

from instorage.main.exceptions import BadRequestException, NotFoundException
from instorage.securitylevels.security_level import SecurityLevel
from instorage.securitylevels.security_level_service import SecurityLevelService
from instorage.ai_models.completion_models.completion_model import CompletionModelSparse
from instorage.ai_models.embedding_models.embedding_model import EmbeddingModelSparse
from instorage.spaces.space_repo import SpaceRepository
from instorage.spaces.space import Space
from instorage.users.user import UserInDB

ModelType = TypeVar("ModelType", CompletionModelSparse, EmbeddingModelSparse)
ModelGetterFn: TypeAlias = Callable[[UUID, bool], ModelType]


class ModelAccess(Protocol):
    """Protocol defining the interface for accessing AI models."""

    async def get_completion_model(
        self, id: UUID, include_non_accessible: bool = False
    ) -> CompletionModelSparse:
        """Get a completion model by ID."""
        ...

    async def get_embedding_model(
        self, id: UUID, include_non_accessible: bool = False
    ) -> EmbeddingModelSparse:
        """Get an embedding model by ID."""
        ...


@dataclass
class AffectedSpace:
    space_id: UUID
    old_completion_models: List[CompletionModelSparse]
    old_embedding_models: List[EmbeddingModelSparse]
    new_completion_models: List[CompletionModelSparse]
    new_embedding_models: List[EmbeddingModelSparse]

    @property
    def removed_completion_models(self) -> List[CompletionModelSparse]:
        return [
            m for m in self.old_completion_models if m not in self.new_completion_models
        ]

    @property
    def removed_embedding_models(self) -> List[EmbeddingModelSparse]:
        return [
            m for m in self.old_embedding_models if m not in self.new_embedding_models
        ]

    @property
    def added_completion_models(self) -> List[CompletionModelSparse]:
        return [
            m for m in self.new_completion_models if m not in self.old_completion_models
        ]

    @property
    def added_embedding_models(self) -> List[EmbeddingModelSparse]:
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

    affected_space: Optional[
        AffectedSpace
    ]  # Detailed information about the affected space
    warning: Optional[str] = None


class SecurityLevelOrchestrator:
    """
    Orchestrates security level operations by coordinating between services.
    Handles analysis and validation of security level changes across the system.
    """

    def __init__(
        self,
        user: UserInDB,
        security_level_service: SecurityLevelService,
        model_access: ModelAccess,
        space_repo: SpaceRepository,
    ):
        self.user = user
        self.security_level_service = security_level_service
        self.model_access = model_access
        self.space_repo = space_repo

    async def _analyze_models_for_security_level(
        self,
        models: List[ModelType],
        new_security_level: Optional[SecurityLevel],
        get_full_model_fn: ModelGetterFn[ModelType],
    ) -> Tuple[List[ModelType], List[ModelType]]:
        """
        Pure function to analyze which models would become unavailable and which would be added.

        Args:
            models: List of models to analyze
            new_security_level: The new security level to check against
            get_full_model_fn: Function to get the full model by ID

        Returns:
            Tuple of (available models, unavailable models)
        """
        available: List[ModelType] = []
        unavailable: List[ModelType] = []

        for model in models:
            full_model = await get_full_model_fn(model.id, include_non_accessible=True)

            # If no new security level, all models are available
            if not new_security_level:
                available.append(model)
                continue

            # If model has no security level, it's unavailable
            if not full_model.security_level:
                unavailable.append(model)
                continue

            # If new security level is lower or equal to model's security level,
            # the model remains available
            if full_model.security_level.value >= new_security_level.value:
                available.append(model)
            else:
                unavailable.append(model)

        return available, unavailable

    async def _analyze_security_level_change(
        self,
        current_security_level: Optional[SecurityLevel],
        new_security_level: Optional[SecurityLevel],
        space_id: Optional[UUID],
    ) -> SecurityLevelChangeAnalysis:
        """Analyze the impact of changing security levels."""
        affected_spaces: List[AffectedSpace] = []

        if space_id:
            # Analyzing single space
            space = await self.space_repo.get(space_id)
            if not space:
                return SecurityLevelChangeAnalysis(
                    current_security_level=current_security_level,
                    new_security_level=new_security_level,
                    affected_spaces=[],
                )

            # Check which models will be affected
            (
                available_completion_models,
                unavailable_completion_models,
            ) = await self._analyze_models_for_security_level(
                space.completion_models,
                new_security_level,
                self.model_access.get_completion_model,
            )

            (
                available_embedding_models,
                unavailable_embedding_models,
            ) = await self._analyze_models_for_security_level(
                space.embedding_models,
                new_security_level,
                self.model_access.get_embedding_model,
            )

            affected_space = AffectedSpace(
                space_id=space.id,
                old_completion_models=space.completion_models,
                old_embedding_models=space.embedding_models,
                new_completion_models=available_completion_models,
                new_embedding_models=available_embedding_models,
            )

            if affected_space.did_change():
                affected_spaces.append(affected_space)
        else:
            # Analyzing security level change itself - need to check all spaces
            if not current_security_level:
                return SecurityLevelChangeAnalysis(
                    current_security_level=None,
                    new_security_level=new_security_level,
                    affected_spaces=[],
                )

            spaces = await self.space_repo.get_spaces_by_security_level(
                current_security_level.id
            )

            for space in spaces:
                (
                    available_completion_models,
                    unavailable_completion_models,
                ) = await self._analyze_models_for_security_level(
                    space.completion_models,
                    new_security_level,
                    self.model_access.get_completion_model,
                )
                (
                    available_embedding_models,
                    unavailable_embedding_models,
                ) = await self._analyze_models_for_security_level(
                    space.embedding_models,
                    new_security_level,
                    self.model_access.get_embedding_model,
                )

                affected_space = AffectedSpace(
                    space_id=space.id,
                    old_completion_models=space.completion_models,
                    old_embedding_models=space.embedding_models,
                    new_completion_models=available_completion_models,
                    new_embedding_models=available_embedding_models,
                )

                if affected_space.did_change():
                    affected_spaces.append(affected_space)

        return SecurityLevelChangeAnalysis(
            current_security_level=current_security_level,
            new_security_level=new_security_level,
            affected_spaces=affected_spaces,
        )

    async def _analyze_security_level_update(
        self,
        current_level: SecurityLevel,
        new_value: Optional[int] = None,
    ) -> SecurityLevelChangeAnalysis:
        """Analyze impact of security level changes."""
        # Create temporary security level with new value for analysis
        new_security_level = SecurityLevel(
            id=current_level.id,
            name=current_level.name,
            description=current_level.description,
            value=new_value if new_value is not None else current_level.value,
            tenant_id=current_level.tenant_id,
        )

        return await self._analyze_security_level_change(
            current_security_level=current_level,
            new_security_level=new_security_level,
            space_id=None,  # Analyze all spaces
        )

    async def analyze_space_security_level_change(
        self,
        space_id: UUID,
        current_security_level: Optional[SecurityLevel],
        new_security_level: Optional[SecurityLevel],
    ) -> SpaceSecurityAnalysisResponse:
        """
        Analyze the impact of changing a space's security level.
        This is used when updating a space's security level to understand the impact
        on the space's models.
        """
        analysis = await self._analyze_security_level_change(
            current_security_level=current_security_level,
            new_security_level=new_security_level,
            space_id=space_id,
        )

        warning = None
        if analysis.affected_spaces:
            warning = f"This change will make {len(analysis.affected_spaces)} spaces' models unavailable"

        return SpaceSecurityAnalysisResponse(
            affected_space=analysis.affected_spaces[0]
            if analysis.affected_spaces
            else None,
            warning=warning,
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
        analysis = await self._analyze_security_level_update(created)
        warning = None
        if analysis and analysis.affected_spaces:
            warning = f"This security level will affect {len(analysis.affected_spaces)} spaces"

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
            analysis = await self._analyze_security_level_update(current, value)
            if analysis and analysis.affected_spaces:
                warning = (
                    f"This change will affect {len(analysis.affected_spaces)} spaces"
                )

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

    async def delete_security_level(self, id: UUID) -> None:
        """Delete a security level with impact analysis."""
        # Get current security level
        current = await self.security_level_service.get_security_level(id)

        # Analyze impact before deletion
        analysis = await self._analyze_security_level_update(current)
        if analysis and analysis.affected_spaces:
            raise BadRequestException(
                f"Cannot delete security level as it is used by {len(analysis.affected_spaces)} spaces"
            )

        # Perform the deletion
        await self.security_level_service.delete_security_level(id)

    async def analyze_security_level_update(
        self,
        id: UUID,
        value: Optional[int] = None,
    ) -> SecurityLevelChangeAnalysis:
        """
        Analyze the impact of updating a security level's properties without applying changes.
        Currently supports:
        - Value changes: Shows which spaces and models would be affected
        """
        security_level = await self.security_level_service.get_security_level(id)
        if value is None:
            value = security_level.value

        return await self._analyze_security_level_update(security_level, value)

    async def _get_filtered_model_ids(
        self,
        current_models: List[CompletionModelSparse | EmbeddingModelSparse],
        affected_space: Optional[AffectedSpace],
    ) -> List[UUID]:
        """Helper to get IDs of models that will remain available."""
        if not affected_space:
            return [model.id for model in current_models]

        removed_ids: Set[UUID] = {
            model.id
            for model in affected_space.removed_completion_models
            + affected_space.removed_embedding_models
        }
        return [model.id for model in current_models if model.id not in removed_ids]

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
        if security_level_id is None or (
            space.security_level and security_level_id == space.security_level.id
        ):
            return space

        # Get the new security level
        new_security_level: Optional[SecurityLevel] = None
        if security_level_id is not None:
            new_security_level = await self.security_level_service.get_security_level(
                security_level_id
            )

        # Analyze impact and filter models
        analysis = await self._analyze_security_level_change(
            current_security_level=space.security_level,
            new_security_level=new_security_level,
            space_id=space_id,
        )

        # Find the affected space info for this space
        affected_space = next(
            (space for space in analysis.affected_spaces if space.space_id == space_id),
            None,
        )

        # If space is affected, use the new model lists from the analysis
        filtered_completion_models: List[CompletionModelSparse]
        filtered_embedding_models: List[EmbeddingModelSparse]

        if affected_space:
            filtered_completion_models = affected_space.new_completion_models
            filtered_embedding_models = affected_space.new_embedding_models
        else:
            # If not affected, keep current models
            filtered_completion_models = space.completion_models
            filtered_embedding_models = space.embedding_models

        # Update the space
        space.update(
            security_level=new_security_level,
            completion_models=filtered_completion_models,
            embedding_models=filtered_embedding_models,
        )

        return await self.space_repo.update(space)
