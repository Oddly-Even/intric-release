from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
import itertools
from pydantic import BaseModel, ValidationError
import pytest
from typing import TypeVar, Generic, Type, Iterable
from instorage.securitylevels.security_level_analysis import (
    SecurityLevel,
    Space,
    CompletionModel,
    EmbeddingModel,
    SpaceChange,
    Environment,
    EnvironmentUpdate,
    EnvironmentChange,
    _get_id,
    _get_id_or_none,
)


class LevelSpec(BaseModel, frozen=True):
    value: int | None
    display_name: str


LOW = LevelSpec(value=10, display_name="Low")
MEDIUM = LevelSpec(value=50, display_name="Medium")
HIGH = LevelSpec(value=100, display_name="High")

T = TypeVar("T")


def flatten(iterable: Iterable[Iterable[T]]) -> list[T]:
    return list(itertools.chain(*iterable))


def new_level(spec: LevelSpec) -> SecurityLevel:
    id = uuid4()
    name = f"{spec.display_name} {id}"
    return SecurityLevel(id=id, name=name, value=spec.value)


def new_levels(
    spec_counts: dict[LevelSpec, int],
) -> dict[LevelSpec, list[SecurityLevel]]:
    return {
        spec: [new_level(spec) for _ in range(count)]
        for spec, count in spec_counts.items()
    }


def new_space(security_level: SecurityLevel | None) -> Space:
    id = uuid4()
    name = f"Space {id}"
    return Space(
        id=id,
        name=name,
        security_level_id=security_level.id if security_level else None,
    )


def new_completion_model(security_level: SecurityLevel | None) -> CompletionModel:
    id = uuid4()
    name = f"Completion Model {id}"
    return CompletionModel(
        id=id,
        name=name,
        security_level_id=security_level.id if security_level else None,
    )


def new_embedding_model(security_level: SecurityLevel | None) -> EmbeddingModel:
    id = uuid4()
    name = f"Embedding Model {id}"
    return EmbeddingModel(
        id=id,
        name=name,
        security_level_id=security_level.id if security_level else None,
    )


def test_get_id():
    id = uuid4()
    assert _get_id(id) == id
    level = new_level(LOW)
    assert _get_id(level) == level.id
    with pytest.raises(ValueError, match="Item is None"):
        _get_id(None)

    assert _get_id_or_none(None) is None
    assert _get_id_or_none(id) == id
    assert _get_id_or_none(level) == level.id


def test_environment_validation_duplicate_security_levels():
    level = new_level(LOW)
    completion_model = new_completion_model(level)
    embedding_model = new_embedding_model(level)
    space = new_space(level)

    duplicate_level = SecurityLevel(id=level.id, name="Duplicate", value=level.value)
    with pytest.raises(ValidationError, match="Duplicate security level IDs found"):
        Environment(
            security_levels=[level, duplicate_level],
            spaces=[space],
            completion_models=[completion_model],
            embedding_models=[embedding_model],
        )


def test_environment_validation_duplicate_spaces():
    level = new_level(LOW)
    completion_model = new_completion_model(level)
    embedding_model = new_embedding_model(level)
    space = new_space(level)

    duplicate_space = Space(id=space.id, name="Duplicate", security_level_id=None)
    with pytest.raises(ValidationError, match="Duplicate space IDs found"):
        Environment(
            security_levels=[level],
            spaces=[space, duplicate_space],
            completion_models=[completion_model],
            embedding_models=[embedding_model],
        )


def test_environment_validation_duplicate_completion_models():
    level = new_level(LOW)
    completion_model = new_completion_model(level)
    embedding_model = new_embedding_model(level)
    space = new_space(level)

    duplicate_completion_model = CompletionModel(
        id=completion_model.id, name="Duplicate", security_level_id=None
    )
    with pytest.raises(ValidationError, match="Duplicate completion model IDs found"):
        Environment(
            security_levels=[level],
            spaces=[space],
            completion_models=[completion_model, duplicate_completion_model],
            embedding_models=[embedding_model],
        )


def test_environment_validation_duplicate_embedding_models():
    level = new_level(LOW)
    completion_model = new_completion_model(level)
    embedding_model = new_embedding_model(level)
    space = new_space(level)

    duplicate_embedding_model = EmbeddingModel(
        id=embedding_model.id, name="Duplicate", security_level_id=None
    )
    with pytest.raises(ValidationError, match="Duplicate embedding model IDs found"):
        Environment(
            security_levels=[level],
            spaces=[space],
            completion_models=[completion_model],
            embedding_models=[embedding_model, duplicate_embedding_model],
        )


def test_environment_modifications():
    # Create security levels
    levels = new_levels({LOW: 1, MEDIUM: 1, HIGH: 1})
    level_low = levels[LOW][0]
    level_medium = levels[MEDIUM][0]
    level_high = levels[HIGH][0]

    # Create spaces with different security levels
    space_low = new_space(level_low)
    space_medium = new_space(level_medium)
    space_none = new_space(None)

    # Create models with different security levels
    completion_low = new_completion_model(level_low)
    completion_high = new_completion_model(level_high)
    embedding_medium = new_embedding_model(level_medium)
    embedding_none = new_embedding_model(None)

    # Create environment
    env = Environment(
        security_levels=flatten(levels.values()),
        spaces=[space_low, space_medium, space_none],
        completion_models=[completion_low, completion_high],
        embedding_models=[embedding_medium, embedding_none],
    )

    # Remove medium security level
    env_medium_removed = env.modified_environment(remove_security_levels=[level_medium])
    assert env_medium_removed == Environment(
        security_levels=[level_low, level_high],
        spaces=[space_low, space_medium.with_level(None), space_none],
        completion_models=[completion_low, completion_high],
        embedding_models=[embedding_medium.with_level(None), embedding_none],
    )

    # Remove high security level
    env_high_removed = env.modified_environment(remove_security_levels=[level_high])
    assert env_high_removed == Environment(
        security_levels=[level_low, level_medium],
        spaces=[space_low, space_medium, space_none],
        completion_models=[completion_low, completion_high.with_level(None)],
        embedding_models=[embedding_medium, embedding_none],
    )

    # Add another medium security level and assign low space to it
    level_medium_2 = new_level(MEDIUM)
    env_medium_added = env.modified_environment(
        security_levels=[level_medium, level_medium_2],
        spaces=[space_low.with_level(level_medium_2)],
    )
    assert env_medium_added == Environment(
        security_levels=[level_low, level_medium, level_high, level_medium_2],
        spaces=[space_low.with_level(level_medium_2), space_medium, space_none],
        completion_models=[completion_low, completion_high],
        embedding_models=[embedding_medium, embedding_none],
    )

    # Raise all security level values to high
    all_levels_high = [lv.with_value(HIGH) for lv in env.security_levels]
    env_high_raised = env.modified_environment(
        security_levels=all_levels_high,
    )
    assert env_high_raised == Environment(
        security_levels=all_levels_high,
        spaces=[
            space_low,
            space_medium,
            space_none,
        ],
        completion_models=[completion_low, completion_high],
        embedding_models=[embedding_medium, embedding_none],
    )

    # Change security level of completion and embedding models to medium
    env_medium_changed = env.modified_environment(
        completion_models=[completion_low.with_level(level_medium)],
        embedding_models=[embedding_none.with_level(level_medium)],
    )
    assert env_medium_changed == Environment(
        security_levels=[level_low, level_medium, level_high],
        spaces=[space_low, space_medium, space_none],
        completion_models=[completion_low.with_level(level_medium), completion_high],
        embedding_models=[embedding_medium, embedding_none.with_level(level_medium)],
    )


def test_environment_access():
    # Create security levels
    level_low = new_level(LOW)
    level_medium = new_level(MEDIUM)
    level_high = new_level(HIGH)

    # Create spaces
    space_none = new_space(None)
    space_low = new_space(level_low)
    space_high = new_space(level_high)

    # Create models
    completion_none = new_completion_model(None)
    completion_low = new_completion_model(level_low)
    completion_high = new_completion_model(level_high)
    embedding_none = new_embedding_model(None)
    embedding_medium = new_embedding_model(level_medium)

    # Create environment
    env = Environment(
        security_levels=[level_low, level_medium, level_high],
        spaces=[space_low, space_high, space_none],
        completion_models=[completion_none, completion_low, completion_high],
        embedding_models=[embedding_none, embedding_medium],
    )

    access = env.get_access()

    assert access.is_allowed_only(space_none, [completion_none, embedding_none])
    assert access.is_allowed_only(
        space_low, [completion_low, completion_high, embedding_medium]
    )
    assert access.is_allowed_only(space_high, [completion_high])

    # Negative test
    assert not access.is_allowed_only(space_low, [completion_none, embedding_none])
    assert not access.is_allowed_only(space_low, [completion_low, embedding_none])
    assert not access.is_allowed_only(space_high, [completion_high, embedding_medium])


def test_environment_update_changes():
    # Create security levels
    levels = new_levels({LOW: 2, MEDIUM: 1})
    level_low = levels[LOW][0]
    level_low_2 = levels[LOW][1]
    level_medium = levels[MEDIUM][0]

    # Create spaces and models for old environment
    space_low = new_space(level_low)
    space_medium = new_space(level_medium)
    completion_low = new_completion_model(level_low)
    embedding_low = new_embedding_model(level_low)
    completion_low_2 = new_completion_model(level_low_2)
    embedding_low_2 = new_embedding_model(level_low_2)

    old_env = Environment(
        security_levels=flatten(levels.values()),
        spaces=[space_low, space_medium],
        completion_models=[completion_low, completion_low_2],
        embedding_models=[embedding_low, embedding_low_2],
    )

    # Create new environment with medium security level for space
    space_low_raised = space_low.with_level(level_medium)
    new_env = old_env.modified_environment(
        spaces=[space_low_raised],
    )
    update = EnvironmentUpdate(old_environment=old_env, new_environment=new_env)
    changes = update.get_change()
    assert changes == EnvironmentChange(
        changed_spaces=[
            SpaceChange(
                space=space_low_raised,
                added_completion_model_ids=[],
                removed_completion_model_ids=[completion_low.id, completion_low_2.id],
                added_embedding_model_ids=[],
                removed_embedding_model_ids=[embedding_low.id, embedding_low_2.id],
            )
        ]
    )

    # Remove a security level that is in use. What happens here is that a space loses its
    # security level, as do the completion and embedding models that were using the same
    # security level. The space still only loses access to the completion and embedding
    # that still have security levels though, because spaces without security levels are
    # allowed access to models without security levels.
    new_env = old_env.modified_environment(
        remove_security_levels=[level_low],
    )
    update = EnvironmentUpdate(old_environment=old_env, new_environment=new_env)
    changes = update.get_change()
    assert changes == EnvironmentChange(
        changed_spaces=[
            SpaceChange(
                space=space_low.with_level(None),
                added_completion_model_ids=[],
                removed_completion_model_ids=[completion_low_2.id],
                added_embedding_model_ids=[],
                removed_embedding_model_ids=[embedding_low_2.id],
            )
        ]
    )

    # Lower the security level of a space. Should grant access to additional models.
    new_env = old_env.modified_environment(
        spaces=[space_medium.with_level(level_low)],
    )
    update = EnvironmentUpdate(old_environment=old_env, new_environment=new_env)
    changes = update.get_change()

    assert changes == EnvironmentChange(
        changed_spaces=[
            SpaceChange(
                space=space_medium.with_level(level_low),
                added_completion_model_ids=[completion_low.id, completion_low_2.id],
                removed_completion_model_ids=[],
                added_embedding_model_ids=[embedding_low.id, embedding_low_2.id],
                removed_embedding_model_ids=[],
            )
        ]
    )


def test_environment_update_get_latest():
    # Create security levels
    levels = new_levels({LOW: 1, MEDIUM: 2})
    level_low = levels[LOW][0]
    level_medium = levels[MEDIUM][0]
    level_medium_2 = levels[MEDIUM][1]

    # Create spaces and models for old environment
    space_low = new_space(level_low)
    completion_low = new_completion_model(level_low)
    embedding_low = new_embedding_model(level_low)
    completion_medium = new_completion_model(level_medium)
    embedding_medium = new_embedding_model(level_medium)

    old_env = Environment(
        security_levels=flatten(levels.values()),
        spaces=[space_low],
        completion_models=[completion_low],
        embedding_models=[embedding_low],
    )

    completion_none = new_completion_model(None)
    env = old_env.modified_environment(
        completion_models=[
            completion_none,
            completion_medium.with_level(level_medium_2),
        ],
        embedding_models=[embedding_medium.with_level(level_medium_2)],
        remove_security_levels=[level_low],
        remove_spaces=[space_low],
        remove_completion_models=[completion_low],
        remove_embedding_models=[embedding_low],
    )

    update = EnvironmentUpdate(old_environment=old_env, new_environment=env)

    # We can get models that were removed
    assert update.get_latest_model(completion_low) == completion_low
    assert update.get_latest_model(embedding_low) == embedding_low

    # We can get models that were updated, and get the updated models
    assert update.get_latest_model(completion_medium) == completion_medium.with_level(
        level_medium_2
    )
    assert update.get_latest_model(embedding_medium) == embedding_medium.with_level(
        level_medium_2
    )

    # We can get models that were added
    assert update.get_latest_model(completion_none) == completion_none
