from typing import Optional, Set
from uuid import UUID
from pydantic import BaseModel, field_validator


class SecurityLevel(BaseModel, frozen=True):
    id: UUID
    name: str
    value: int


class Space(BaseModel, frozen=True):
    id: UUID
    name: str
    security_level_id: Optional[UUID]


class CompletionModel(BaseModel, frozen=True):
    id: UUID
    name: str
    security_level_id: Optional[UUID]


class EmbeddingModel(BaseModel, frozen=True):
    id: UUID
    name: str
    security_level_id: Optional[UUID]


class SpaceChange(BaseModel, frozen=True):
    space: Space
    old_security_level_id: Optional[UUID]
    new_security_level_id: Optional[UUID]
    added_completion_models: Set[CompletionModel]
    removed_completion_models: Set[CompletionModel]
    added_embedding_models: Set[EmbeddingModel]
    removed_embedding_models: Set[EmbeddingModel]

    def model_availability_changed(self) -> bool:
        return (
            self.added_completion_models
            or self.removed_completion_models
            or self.added_embedding_models
            or self.removed_embedding_models
        )

    def __hash__(self) -> int:
        # Create a hashable representation using immutable types
        return hash(
            (
                self.space,
                self.old_security_level_id,
                self.new_security_level_id,
                tuple(sorted(str(m.id) for m in self.added_completion_models)),
                tuple(sorted(str(m.id) for m in self.removed_completion_models)),
                tuple(sorted(str(m.id) for m in self.added_embedding_models)),
                tuple(sorted(str(m.id) for m in self.removed_embedding_models)),
            )
        )


class SecurityLevelChange(BaseModel, frozen=True):
    security_level: SecurityLevel
    old_value: int
    new_value: int


class CompletionModelChange(BaseModel, frozen=True):
    completion_model: CompletionModel
    old_security_level_id: Optional[UUID]
    new_security_level_id: Optional[UUID]


class EmbeddingModelChange(BaseModel, frozen=True):
    embedding_model: EmbeddingModel
    old_security_level_id: Optional[UUID]
    new_security_level_id: Optional[UUID]


class Changes(BaseModel, frozen=True):
    changed_spaces: Set[SpaceChange]
    added_security_levels: Set[SecurityLevel]
    removed_security_levels: Set[SecurityLevel]
    changed_security_levels: Set[SecurityLevelChange]
    changed_completion_models: Set[CompletionModelChange]
    changed_embedding_models: Set[EmbeddingModelChange]


class Environment(BaseModel, frozen=True):
    security_levels: Set[SecurityLevel]
    spaces: Set[Space]
    completion_models: Set[CompletionModel]
    embedding_models: Set[EmbeddingModel]

    @field_validator("security_levels")
    def validate_unique_security_level_ids(cls, v: Set[SecurityLevel]) -> Set[SecurityLevel]:
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
    def validate_unique_completion_model_ids(cls, v: Set[CompletionModel]) -> Set[CompletionModel]:
        ids = [m.id for m in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate completion model IDs found")
        return v

    @field_validator("embedding_models")
    def validate_unique_embedding_model_ids(cls, v: Set[EmbeddingModel]) -> Set[EmbeddingModel]:
        ids = [m.id for m in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate embedding model IDs found")
        return v


class EnvironmentUpdate(BaseModel, frozen=True):
    old_environment: Environment
    new_environment: Environment

    def get_changes(self) -> Changes:
        # Find security level changes
        old_security_levels = {sl.id: sl for sl in self.old_environment.security_levels}
        new_security_levels = {sl.id: sl for sl in self.new_environment.security_levels}

        added_security_levels = {
            sl
            for sl in self.new_environment.security_levels
            if sl.id not in old_security_levels
        }
        removed_security_levels = {
            sl
            for sl in self.old_environment.security_levels
            if sl.id not in new_security_levels
        }
        changed_security_levels = {
            SecurityLevelChange(
                security_level=new_security_levels[sl_id],
                old_value=old_security_levels[sl_id].value,
                new_value=new_security_levels[sl_id].value,
            )
            for sl_id in old_security_levels.keys() & new_security_levels.keys()
            if old_security_levels[sl_id].value != new_security_levels[sl_id].value
        }

        # Find completion model changes
        old_completion_models = {
            cm.id: cm for cm in self.old_environment.completion_models
        }
        new_completion_models = {
            cm.id: cm for cm in self.new_environment.completion_models
        }
        changed_completion_models = {
            CompletionModelChange(
                completion_model=new_completion_models[cm_id],
                old_security_level_id=old_completion_models[cm_id].security_level_id,
                new_security_level_id=new_completion_models[cm_id].security_level_id,
            )
            for cm_id in old_completion_models.keys() & new_completion_models.keys()
            if old_completion_models[cm_id].security_level_id
            != new_completion_models[cm_id].security_level_id
        }

        # Find embedding model changes
        old_embedding_models = {
            em.id: em for em in self.old_environment.embedding_models
        }
        new_embedding_models = {
            em.id: em for em in self.new_environment.embedding_models
        }

        changed_embedding_models = {
            EmbeddingModelChange(
                embedding_model=new_embedding_models[em_id],
                old_security_level_id=old_embedding_models[em_id].security_level_id,
                new_security_level_id=new_embedding_models[em_id].security_level_id,
            )
            for em_id in old_embedding_models.keys() & new_embedding_models.keys()
            if old_embedding_models[em_id].security_level_id
            != new_embedding_models[em_id].security_level_id
        }

        # Find space changes
        old_spaces = {s.id: s for s in self.old_environment.spaces}
        new_spaces = {s.id: s for s in self.new_environment.spaces}

        changed_spaces = set()
        for space_id in old_spaces.keys() | new_spaces.keys():
            old_space = old_spaces.get(space_id)
            new_space = new_spaces.get(space_id)

            if not new_space:  # Space was removed
                continue
            if not old_space:  # Space was added
                old_space = Space(
                    id=new_space.id, name=new_space.name, security_level_id=None
                )

            # Calculate model changes for the space
            old_allowed_completion_models = {
                m
                for m in self.old_environment.completion_models
                if self._is_model_allowed_in_space(
                    m.security_level_id, old_space.security_level_id
                )
            }
            new_allowed_completion_models = {
                m
                for m in self.new_environment.completion_models
                if self._is_model_allowed_in_space(
                    m.security_level_id, new_space.security_level_id
                )
            }

            old_allowed_embedding_models = {
                m
                for m in self.old_environment.embedding_models
                if self._is_model_allowed_in_space(
                    m.security_level_id, old_space.security_level_id
                )
            }
            new_allowed_embedding_models = {
                m
                for m in self.new_environment.embedding_models
                if self._is_model_allowed_in_space(
                    m.security_level_id, new_space.security_level_id
                )
            }

            space_change = SpaceChange(
                space=new_space,
                old_security_level_id=old_space.security_level_id,
                new_security_level_id=new_space.security_level_id,
                added_completion_models=new_allowed_completion_models
                - old_allowed_completion_models,
                removed_completion_models=old_allowed_completion_models
                - new_allowed_completion_models,
                added_embedding_models=new_allowed_embedding_models
                - old_allowed_embedding_models,
                removed_embedding_models=old_allowed_embedding_models
                - new_allowed_embedding_models,
            )

            if (
                space_change.old_security_level_id != space_change.new_security_level_id
                or space_change.model_availability_changed()
            ):
                changed_spaces.add(space_change)

        return Changes(
            changed_spaces=changed_spaces,
            added_security_levels=added_security_levels,
            removed_security_levels=removed_security_levels,
            changed_security_levels=changed_security_levels,
            changed_completion_models=changed_completion_models,
            changed_embedding_models=changed_embedding_models,
        )

    def _is_model_allowed_in_space(
        self,
        model_security_level_id: Optional[UUID],
        space_security_level_id: Optional[UUID],
    ) -> bool:
        # If both the model and space have no security level, the model is allowed
        if model_security_level_id is None and space_security_level_id is None:
            return True

        # If either the model or space has no security level, the model is not allowed
        if model_security_level_id is None or space_security_level_id is None:
            return False

        # If either security level has been removed, the model is not allowed
        try:
            model_level = next(
                sl.value
                for sl in self.new_environment.security_levels
                if sl.id == model_security_level_id
            )
            space_level = next(
                sl.value
                for sl in self.new_environment.security_levels
                if sl.id == space_security_level_id
            )
        except StopIteration:
            return False

        # Model is allowed if its security level is greater than or equal to the space's level
        return model_level >= space_level
