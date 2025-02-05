from typing import List, Optional, Set, TypeVar, Callable
from uuid import UUID
from pydantic import BaseModel, field_validator

T = TypeVar("T", bound=BaseModel)


class SecurityLevel(BaseModel):
    id: UUID
    name: str
    value: int

    def with_value(self, level: int) -> "SecurityLevel":
        return self.model_copy(update={"value": level})


class Space(BaseModel):
    id: UUID
    name: str
    security_level_id: UUID | None = None

    def with_level(self, security_level: UUID | SecurityLevel | None) -> "Space":
        return self.model_copy(
            update={"security_level_id": _get_id_or_none(security_level)}
        )


class CompletionModel(BaseModel):
    id: UUID
    name: str
    security_level_id: UUID | None = None

    def with_level(
        self, security_level: UUID | SecurityLevel | None
    ) -> "CompletionModel":
        return self.model_copy(
            update={"security_level_id": _get_id_or_none(security_level)}
        )


class EmbeddingModel(BaseModel):
    id: UUID
    name: str
    security_level_id: UUID | None = None

    def with_level(
        self, security_level: UUID | SecurityLevel | None
    ) -> "EmbeddingModel":
        return self.model_copy(
            update={"security_level_id": _get_id_or_none(security_level)}
        )


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

    def is_allowed_only(
        self, space: UUID | Space, models: List[CompletionModel | EmbeddingModel]
    ) -> bool:
        space_id = _get_id(space)

        expected_allowed_completion_models = {
            m.id for m in models if isinstance(m, CompletionModel)
        }
        actual_allowed_completion_models = {
            m.completion_model_id
            for m in self.completion_model_access
            if m.space_id == space_id and m.allowed
        }

        expected_allowed_embedding_models = {
            m.id for m in models if isinstance(m, EmbeddingModel)
        }
        actual_allowed_embedding_models = {
            m.embedding_model_id
            for m in self.embedding_model_access
            if m.space_id == space_id and m.allowed
        }

        if expected_allowed_completion_models != actual_allowed_completion_models:
            return False

        if expected_allowed_embedding_models != actual_allowed_embedding_models:
            return False

        return True


class Environment(BaseModel):
    security_levels: List[SecurityLevel] = []
    spaces: List[Space] = []
    completion_models: List[CompletionModel] = []
    embedding_models: List[EmbeddingModel] = []

    def modified_environment(
        self,
        security_levels: Optional[List[SecurityLevel]] = None,
        spaces: Optional[List[Space]] = None,
        completion_models: Optional[List[CompletionModel]] = None,
        embedding_models: Optional[List[EmbeddingModel]] = None,
        remove_security_levels: Optional[List[UUID | SecurityLevel]] = None,
        remove_spaces: Optional[List[UUID | Space]] = None,
        remove_completion_models: Optional[List[UUID | CompletionModel]] = None,
        remove_embedding_models: Optional[List[UUID | EmbeddingModel]] = None,
    ) -> "Environment":
        """Create a new environment with the given modifications.

        Args:
            security_levels: List of security levels to add or update (based on the `id` field).
            spaces: List of spaces to add or update (based on the `id` field).
            completion_models: List of completion models to add or update (based on the `id` field).
            embedding_models: List of embedding models to add or update (based on the `id` field).
            remove_security_levels: List of security levels to remove.
            remove_spaces: List of spaces to remove.
            remove_completion_models: List of completion models to remove.
            remove_embedding_models: List of embedding models to remove.
        """

        new_environment = self.model_copy(deep=True)
        _modify_pool(
            _update_security_level,
            new_environment.security_levels,
            security_levels,
            remove_security_levels,
        )
        _modify_pool(
            _update_space,
            new_environment.spaces,
            spaces,
            remove_spaces,
        )
        _modify_pool(
            _update_completion_model,
            new_environment.completion_models,
            completion_models,
            remove_completion_models,
        )
        _modify_pool(
            _update_embedding_model,
            new_environment.embedding_models,
            embedding_models,
            remove_embedding_models,
        )

        # Now look for spaces or models that use removed security levels and set their security level to None.
        removed_security_level_ids = {
            _get_id(sl) for sl in remove_security_levels or []
        }
        for space in new_environment.spaces:
            if space.security_level_id in removed_security_level_ids:
                space.security_level_id = None
        for completion_model in new_environment.completion_models:
            if completion_model.security_level_id in removed_security_level_ids:
                completion_model.security_level_id = None
        for embedding_model in new_environment.embedding_models:
            if embedding_model.security_level_id in removed_security_level_ids:
                embedding_model.security_level_id = None

        return new_environment

    @field_validator("security_levels")
    @classmethod
    def validate_unique_security_level_ids(
        cls, v: List[SecurityLevel]
    ) -> List[SecurityLevel]:
        ids = [sl.id for sl in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate security level IDs found")
        return v

    @field_validator("spaces")
    @classmethod
    def validate_unique_space_ids(cls, v: List[Space]) -> List[Space]:
        ids = [s.id for s in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate space IDs found")
        return v

    @field_validator("completion_models")
    @classmethod
    def validate_unique_completion_model_ids(
        cls, v: List[CompletionModel]
    ) -> List[CompletionModel]:
        ids = [m.id for m in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate completion model IDs found")
        return v

    @field_validator("embedding_models")
    @classmethod
    def validate_unique_embedding_model_ids(
        cls, v: List[EmbeddingModel]
    ) -> List[EmbeddingModel]:
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
    added_completion_model_ids: list[UUID]
    removed_completion_model_ids: list[UUID]
    added_embedding_model_ids: list[UUID]
    removed_embedding_model_ids: list[UUID]


class EnvironmentChange(BaseModel, frozen=True):
    changed_spaces: List[SpaceChange]


class EnvironmentUpdate(BaseModel, frozen=True):
    old_environment: Environment
    new_environment: Environment

    def _get_latest_completion_model(
        self, completion_model_id: UUID | CompletionModel
    ) -> CompletionModel:
        return _get_latest_from_pools(
            completion_model_id,
            [
                self.new_environment.completion_models,
                self.old_environment.completion_models,
            ],
        )

    def _get_latest_embedding_model(
        self, embedding_model_id: UUID | EmbeddingModel
    ) -> EmbeddingModel:
        return _get_latest_from_pools(
            embedding_model_id,
            [
                self.new_environment.embedding_models,
                self.old_environment.embedding_models,
            ],
        )

    def get_latest_model(
        self, model: CompletionModel | EmbeddingModel
    ) -> CompletionModel | EmbeddingModel:
        if isinstance(model, CompletionModel):
            return self._get_latest_completion_model(model)
        elif isinstance(model, EmbeddingModel):
            return self._get_latest_embedding_model(model)
        else:
            raise ValueError(f"Invalid model type: {type(model)}")

    def get_change(self) -> EnvironmentChange:
        # Get access states
        old_access = self.old_environment.get_access()
        new_access = self.new_environment.get_access()

        # Track changes in spaces
        changed_spaces = []
        for space in self.new_environment.spaces:
            # Get allowed access sets for quick lookup
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
            
            # Preserve environment ordering by iterating through models in order
            added_completion_model_ids = [
                model.id 
                for model in self.new_environment.completion_models
                if model.id in new_allowed_completion_model_ids 
                and model.id not in old_allowed_completion_model_ids
            ]
            removed_completion_model_ids = [
                model.id
                for model in self.old_environment.completion_models
                if model.id in old_allowed_completion_model_ids 
                and model.id not in new_allowed_completion_model_ids
            ]

            # Same for embedding models
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
            
            added_embedding_model_ids = [
                model.id
                for model in self.new_environment.embedding_models
                if model.id in new_allowed_embedding_model_ids 
                and model.id not in old_allowed_embedding_model_ids
            ]
            removed_embedding_model_ids = [
                model.id
                for model in self.old_environment.embedding_models
                if model.id in old_allowed_embedding_model_ids 
                and model.id not in new_allowed_embedding_model_ids
            ]

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


def _get_latest_from_pools(item: UUID | BaseModel, pools: List[Set[T]]) -> T:
    for pool in pools:
        if model := next((m for m in pool if m.id == _get_id(item)), None):
            return model
    raise ValueError(f"Model with ID {_get_id(item)} not found in any of the pools")


def _modify_pool(
    update_fn: Callable[[T, T], None],
    pool: List[T],
    new_pool: List[T] | None = None,
    remove_pool: List[UUID | T] | None = None,
) -> None:
    for new in new_pool or []:
        if existing := next((m for m in pool if m.id == new.id), None):
            update_fn(existing, new)
        else:
            pool.append(new)
    for item in remove_pool or []:
        if existing := next((m for m in pool if m.id == _get_id(item)), None):
            pool.remove(existing)


def _update_security_level(old: SecurityLevel, new: SecurityLevel) -> None:
    old.name = new.name
    old.value = new.value


def _update_space(old: Space, new: Space) -> None:
    old.name = new.name
    old.security_level_id = new.security_level_id


def _update_completion_model(old: CompletionModel, new: CompletionModel) -> None:
    old.name = new.name
    old.security_level_id = new.security_level_id


def _update_embedding_model(old: EmbeddingModel, new: EmbeddingModel) -> None:
    old.name = new.name
    old.security_level_id = new.security_level_id


def _get_id(item: UUID | BaseModel) -> UUID:
    if not item:
        raise ValueError("Item is None")
    return item if isinstance(item, UUID) else item.id


def _get_id_or_none(item: UUID | BaseModel | None) -> UUID | None:
    if not item:
        return None
    return item if isinstance(item, UUID) else item.id
