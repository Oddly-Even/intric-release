from typing import List, Set, TypeVar
from uuid import UUID
from pydantic import BaseModel, field_validator

T = TypeVar("T", bound=BaseModel)


class SecurityLevel(BaseModel, frozen=True):
    id: UUID
    name: str
    value: int


class Space(BaseModel, frozen=True):
    id: UUID
    name: str
    security_level_id: UUID | None


class CompletionModel(BaseModel, frozen=True):
    id: UUID
    name: str
    security_level_id: UUID | None


class EmbeddingModel(BaseModel, frozen=True):
    id: UUID
    name: str
    security_level_id: UUID | None


class SpaceCompletionModelAccess(BaseModel, frozen=True):
    space_id: UUID
    completion_model_id: UUID | None
    allowed: bool


class SpaceEmbeddingModelAccess(BaseModel, frozen=True):
    space_id: UUID
    embedding_model_id: UUID | None
    allowed: bool


class SpaceSecurityLevelAccess(BaseModel, frozen=True):
    space_id: UUID
    security_level_id: UUID | None
    allowed: bool


class EnvironmentAccess(BaseModel, frozen=True):
    completion_model_access: List[SpaceCompletionModelAccess]
    embedding_model_access: List[SpaceEmbeddingModelAccess]


class Environment(BaseModel, frozen=True):
    security_levels: Set[SecurityLevel]
    spaces: Set[Space]
    completion_models: Set[CompletionModel]
    embedding_models: Set[EmbeddingModel]

    @field_validator("security_levels")
    def validate_unique_security_level_ids(
        cls, v: Set[SecurityLevel]
    ) -> Set[SecurityLevel]:
        ids = [sl.id for sl in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate security level IDs found")
        return v

    @field_validator("spaces")
    def validate_unique_space_ids(cls, v: Set[Space]) -> Set[Space]:
        ids = [s.id for s in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate space IDs found")
        return v

    @field_validator("completion_models")
    def validate_unique_completion_model_ids(
        cls, v: Set[CompletionModel]
    ) -> Set[CompletionModel]:
        ids = [m.id for m in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate completion model IDs found")
        return v

    @field_validator("embedding_models")
    def validate_unique_embedding_model_ids(
        cls, v: Set[EmbeddingModel]
    ) -> Set[EmbeddingModel]:
        ids = [m.id for m in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate embedding model IDs found")
        return v

    def _get_space_completion_model_access(
        self, completion_model_id: UUID, space_id: UUID
    ) -> SpaceCompletionModelAccess:
        forbidden = SpaceCompletionModelAccess(
            space_id=space_id, completion_model_id=completion_model_id, allowed=False
        )
        allowed = SpaceCompletionModelAccess(
            space_id=space_id, completion_model_id=completion_model_id, allowed=True
        )

        if model := next(
            (m for m in self.completion_models if m.id == completion_model_id), None
        ):
            return (
                allowed
                if self._get_space_security_level_access(
                    model.security_level_id, space_id
                ).allowed
                else forbidden
            )
        return forbidden

    def _get_space_embedding_model_access(
        self, embedding_model_id: UUID, space_id: UUID
    ) -> SpaceEmbeddingModelAccess:
        forbidden = SpaceEmbeddingModelAccess(
            space_id=space_id, embedding_model_id=embedding_model_id, allowed=False
        )
        allowed = SpaceEmbeddingModelAccess(
            space_id=space_id, embedding_model_id=embedding_model_id, allowed=True
        )

        if model := next(
            (m for m in self.embedding_models if m.id == embedding_model_id), None
        ):
            return (
                allowed
                if self._get_space_security_level_access(
                    model.security_level_id, space_id
                ).allowed
                else forbidden
            )
        return forbidden

    def _get_space_security_level_access(
        self, security_level_id: UUID | None, space_id: UUID | None
    ) -> SpaceSecurityLevelAccess:
        forbidden = SpaceSecurityLevelAccess(
            space_id=space_id, security_level_id=security_level_id, allowed=False
        )
        allowed = SpaceSecurityLevelAccess(
            space_id=space_id, security_level_id=security_level_id, allowed=True
        )

        if not space_id:
            return forbidden

        space = next((s for s in self.spaces if s.id == space_id), None)
        if not space:
            return forbidden

        # If the space has no security level, and we're checking if access is allowed
        # to entities without a security level, access is allowed.
        if space.security_level_id is None:
            return allowed if security_level_id is None else forbidden

        # Otherwise if space has a security level, and the entity has no security level,
        # access is forbidden.
        if security_level_id is None:
            return forbidden

        # Otherwise if space has a security level, and the entity has a security level,
        # access is allowed if the entity's security level is greater than or equal to the space's.
        # If either security level is not found, access is forbidden.
        if level := next(
            (sl for sl in self.security_levels if sl.id == security_level_id), None
        ):
            if space_level := next(
                (sl for sl in self.security_levels if sl.id == space.security_level_id),
                None,
            ):
                return allowed if level.value >= space_level.value else forbidden

        return forbidden

    def get_access(self) -> EnvironmentAccess:
        completion_model_access = set()
        embedding_model_access = set()

        for space in self.spaces:
            for completion_model in self.completion_models:
                completion_model_access.add(
                    self._get_space_completion_model_access(
                        completion_model.id, space.id
                    )
                )
            for embedding_model in self.embedding_models:
                embedding_model_access.add(
                    self._get_space_embedding_model_access(embedding_model.id, space.id)
                )

        return EnvironmentAccess(
            completion_model_access=completion_model_access,
            embedding_model_access=embedding_model_access,
        )


class SecurityLevelChange(BaseModel, frozen=True):
    security_level: SecurityLevel
    old_value: int
    new_value: int


class SpaceChange(BaseModel, frozen=True):
    space: Space
    added_completion_model_ids: List[UUID]
    removed_completion_model_ids: List[UUID]
    added_embedding_model_ids: List[UUID]
    removed_embedding_model_ids: List[UUID]


class EnvironmentChange(BaseModel, frozen=True):
    changed_spaces: List[SpaceChange]


class EnvironmentUpdate(BaseModel, frozen=True):
    old_environment: Environment
    new_environment: Environment

    def get_latest_completion_model(self, completion_model_id: UUID) -> CompletionModel:
        return _get_latest_from_pools(
            completion_model_id,
            [
                self.new_environment.completion_models,
                self.old_environment.completion_models,
            ],
        )

    def get_latest_embedding_model(self, embedding_model_id: UUID) -> EmbeddingModel:
        return _get_latest_from_pools(
            embedding_model_id,
            [
                self.new_environment.embedding_models,
                self.old_environment.embedding_models,
            ],
        )

    def get_change(self) -> EnvironmentChange:
        # Get access states
        old_access = self.old_environment.get_access()
        new_access = self.new_environment.get_access()

        # Track changes in spaces
        changed_spaces = []
        for space in self.new_environment.spaces:
            old_allowed_completion_model_ids = {
                m.completion_model_id
                for m in old_access.completion_model_access
                if m.space_id == space.id and m.allowed
            }
            new_allowed_completion_model_ids = {
                m.completion_model_id
                for m in new_access.completion_model_access
                if m.space_id == space.id and m.allowed
            }
            added_completion_model_ids = (
                new_allowed_completion_model_ids - old_allowed_completion_model_ids
            )
            removed_completion_model_ids = (
                old_allowed_completion_model_ids - new_allowed_completion_model_ids
            )

            old_allowed_embedding_model_ids = {
                m.embedding_model_id
                for m in old_access.embedding_model_access
                if m.space_id == space.id and m.allowed
            }
            new_allowed_embedding_model_ids = {
                m.embedding_model_id
                for m in new_access.embedding_model_access
                if m.space_id == space.id and m.allowed
            }
            added_embedding_model_ids = (
                new_allowed_embedding_model_ids - old_allowed_embedding_model_ids
            )
            removed_embedding_model_ids = (
                old_allowed_embedding_model_ids - new_allowed_embedding_model_ids
            )

            if (
                added_completion_model_ids
                or removed_completion_model_ids
                or added_embedding_model_ids
                or removed_embedding_model_ids
            ):
                changed_spaces.append(
                    SpaceChange(
                        space=space,
                        added_completion_model_ids=added_completion_model_ids,
                        removed_completion_model_ids=removed_completion_model_ids,
                        added_embedding_model_ids=added_embedding_model_ids,
                        removed_embedding_model_ids=removed_embedding_model_ids,
                    )
                )

        return EnvironmentChange(
            changed_spaces=changed_spaces,
        )


def _get_latest_from_pools(id: UUID, pools: List[Set[T]]) -> T:
    for pool in pools:
        if model := next((m for m in pool if m.id == id), None):
            return model
    raise ValueError(f"Model with ID {id} not found in any of the pools")
