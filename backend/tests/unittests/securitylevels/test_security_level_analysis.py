from datetime import datetime
from uuid import UUID, uuid4
import pytest
from instorage.securitylevels.security_level_analysis import (
    SecurityLevel,
    Space,
    CompletionModel,
    EmbeddingModel,
    SpaceChange,
    Environment,
    EnvironmentUpdate,
    CompletionModelChange,
    EmbeddingModelChange,
    Changes,
)
from pydantic import ValidationError


@pytest.fixture
def security_levels():
    return {
        SecurityLevel(id=uuid4(), name="Low", value=1),
        SecurityLevel(id=uuid4(), name="Medium", value=2),
        SecurityLevel(id=uuid4(), name="High", value=3),
    }


@pytest.fixture
def low_security_level(security_levels):
    return next(sl for sl in security_levels if sl.value == 1)


@pytest.fixture
def medium_security_level(security_levels):
    return next(sl for sl in security_levels if sl.value == 2)


@pytest.fixture
def high_security_level(security_levels):
    return next(sl for sl in security_levels if sl.value == 3)


@pytest.fixture
def completion_models(low_security_level, medium_security_level):
    return {
        CompletionModel(
            id=uuid4(),
            name="Basic Model",
            security_level_id=low_security_level.id,
        ),
        CompletionModel(
            id=uuid4(),
            name="Advanced Model",
            security_level_id=medium_security_level.id,
        ),
        CompletionModel(
            id=uuid4(),
            name="Unrestricted Model",
            security_level_id=None,
        ),
    }


@pytest.fixture
def embedding_models(low_security_level, high_security_level):
    return {
        EmbeddingModel(
            id=uuid4(),
            name="Basic Embeddings",
            security_level_id=low_security_level.id,
        ),
        EmbeddingModel(
            id=uuid4(),
            name="Secure Embeddings",
            security_level_id=high_security_level.id,
        ),
    }


@pytest.fixture
def spaces(low_security_level, medium_security_level):
    return {
        Space(
            id=uuid4(),
            name="Public Space",
            security_level_id=low_security_level.id,
        ),
        Space(
            id=uuid4(),
            name="Private Space",
            security_level_id=medium_security_level.id,
        ),
        Space(
            id=uuid4(),
            name="Unrestricted Space",
            security_level_id=None,
        ),
    }


@pytest.fixture
def base_environment(
    security_levels: set[SecurityLevel],
    spaces: set[Space],
    completion_models: set[CompletionModel],
    embedding_models: set[EmbeddingModel],
):
    return Environment(
        security_levels=security_levels,
        spaces=spaces,
        completion_models=completion_models,
        embedding_models=embedding_models,
    )


def test_space_change_model_availability(low_security_level: SecurityLevel):
    # Test when no models changed
    space = Space(
        id=uuid4(), name="Test Space", security_level_id=low_security_level.id
    )
    space_change = SpaceChange(
        space=space,
        old_security_level_id=low_security_level.id,
        new_security_level_id=low_security_level.id,
        added_completion_models=set(),
        removed_completion_models=set(),
        added_embedding_models=set(),
        removed_embedding_models=set(),
    )
    assert not space_change.model_availability_changed()

    # Test when models changed
    model = CompletionModel(
        id=uuid4(), name="Test Model", security_level_id=low_security_level.id
    )
    space_change = SpaceChange(
        space=space,
        old_security_level_id=low_security_level.id,
        new_security_level_id=low_security_level.id,
        added_completion_models={model},
        removed_completion_models=set(),
        added_embedding_models=set(),
        removed_embedding_models=set(),
    )
    assert space_change.model_availability_changed()


def test_environment_update_security_level_changes(
    base_environment: Environment,
):
    # Create a new environment with modified security levels
    new_security_level = SecurityLevel(id=uuid4(), name="Very High", value=4)
    modified_security_level: SecurityLevel = next(
        iter(base_environment.security_levels)
    )
    new_modified_security_level = SecurityLevel(
        id=modified_security_level.id,
        name=modified_security_level.name,
        value=modified_security_level.value + 1,
    )

    new_security_levels = base_environment.security_levels - {
        modified_security_level
    } | {new_modified_security_level, new_security_level}

    new_environment = Environment(
        security_levels=new_security_levels,
        spaces=base_environment.spaces,
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models,
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=new_environment,
    )

    changes = env_update.get_changes()

    assert len(changes.added_security_levels) == 1
    assert new_security_level in changes.added_security_levels
    assert len(changes.changed_security_levels) == 1
    changed_level = next(iter(changes.changed_security_levels))
    assert changed_level.security_level == new_modified_security_level
    assert changed_level.old_value == modified_security_level.value
    assert changed_level.new_value == new_modified_security_level.value


def test_environment_update_model_changes(
    base_environment: Environment, high_security_level: SecurityLevel
):
    # Modify security level of a completion model
    old_model: CompletionModel = next(iter(base_environment.completion_models))
    new_model = CompletionModel(
        id=old_model.id,
        name=old_model.name,
        security_level_id=high_security_level.id,
    )

    new_environment = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces,
        completion_models=base_environment.completion_models - {old_model}
        | {new_model},
        embedding_models=base_environment.embedding_models,
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=new_environment,
    )

    changes = env_update.get_changes()

    assert len(changes.changed_completion_models) == 1
    changed_model = next(iter(changes.changed_completion_models))
    assert changed_model.completion_model == new_model
    assert changed_model.old_security_level_id == old_model.security_level_id
    assert changed_model.new_security_level_id == high_security_level.id


def test_model_allowed_in_space(base_environment: Environment):
    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=base_environment,
    )

    # Test unrestricted model in unrestricted space
    assert env_update._is_model_allowed_in_space(None, None)

    # Test restricted model in unrestricted space
    restricted_model: CompletionModel = next(
        m for m in base_environment.completion_models if m.security_level_id is not None
    )
    assert not env_update._is_model_allowed_in_space(
        restricted_model.security_level_id, None
    )

    # Test unrestricted model in restricted space
    restricted_space: Space = next(
        s for s in base_environment.spaces if s.security_level_id is not None
    )
    assert not env_update._is_model_allowed_in_space(
        None, restricted_space.security_level_id
    )

    # Test model with higher security level than space
    high_security_model: EmbeddingModel = next(
        m for m in base_environment.embedding_models if m.security_level_id is not None
    )
    low_security_space: Space = next(
        s for s in base_environment.spaces if s.security_level_id is not None
    )
    assert env_update._is_model_allowed_in_space(
        high_security_model.security_level_id,
        low_security_space.security_level_id,
    )


def test_space_changes_with_model_availability(
    base_environment: Environment, high_security_level: SecurityLevel
):
    # Modify a space's security level to affect model availability
    old_space: Space = next(iter(base_environment.spaces))
    new_space = Space(
        id=old_space.id,
        name=old_space.name,
        security_level_id=high_security_level.id,
    )

    new_environment = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces - {old_space} | {new_space},
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models,
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=new_environment,
    )

    changes = env_update.get_changes()

    assert len(changes.changed_spaces) == 1
    space_change: SpaceChange = next(iter(changes.changed_spaces))
    assert space_change.space == new_space
    assert space_change.old_security_level_id == old_space.security_level_id
    assert space_change.new_security_level_id == high_security_level.id
    # Verify that model availability changed due to security level change
    assert space_change.model_availability_changed()


def test_space_changes_for_added_and_removed_spaces(
    base_environment: Environment, high_security_level: SecurityLevel
):
    # Test space addition
    new_space = Space(
        id=uuid4(),
        name="New Space",
        security_level_id=high_security_level.id,
    )

    # Environment with added space
    env_with_added_space = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces | {new_space},
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models,
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=env_with_added_space,
    )

    changes = env_update.get_changes()
    added_space_changes = [
        c for c in changes.changed_spaces if c.space.id == new_space.id
    ]
    assert len(added_space_changes) == 1
    assert added_space_changes[0].old_security_level_id is None
    assert added_space_changes[0].new_security_level_id == high_security_level.id

    # Test space removal
    removed_space: Space = next(iter(base_environment.spaces))
    env_with_removed_space = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces - {removed_space},
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models,
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=env_with_removed_space,
    )

    changes = env_update.get_changes()
    # Verify that removed spaces are not included in changes
    removed_space_changes = [
        c for c in changes.changed_spaces if c.space.id == removed_space.id
    ]
    assert len(removed_space_changes) == 0


def test_model_changes_with_different_security_levels(base_environment: Environment):
    # Test changing model from unrestricted to restricted
    unrestricted_model: CompletionModel = next(
        m for m in base_environment.completion_models if m.security_level_id is None
    )
    new_security_level: SecurityLevel = next(iter(base_environment.security_levels))

    restricted_model = CompletionModel(
        id=unrestricted_model.id,
        name=unrestricted_model.name,
        security_level_id=new_security_level.id,
    )

    new_environment = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces,
        completion_models=base_environment.completion_models - {unrestricted_model}
        | {restricted_model},
        embedding_models=base_environment.embedding_models,
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=new_environment,
    )

    changes = env_update.get_changes()
    assert len(changes.changed_completion_models) == 1
    model_change: CompletionModelChange = next(iter(changes.changed_completion_models))
    assert model_change.old_security_level_id is None
    assert model_change.new_security_level_id == new_security_level.id


def test_security_level_removal(base_environment):
    # Remove a security level that's in use
    security_level_to_remove: SecurityLevel = next(
        iter(base_environment.security_levels)
    )

    new_environment = Environment(
        security_levels=base_environment.security_levels - {security_level_to_remove},
        spaces=base_environment.spaces,
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models,
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=new_environment,
    )

    changes = env_update.get_changes()
    assert len(changes.removed_security_levels) == 1
    assert security_level_to_remove in changes.removed_security_levels


def test_model_availability_in_space_with_security_changes(
    base_environment: Environment, high_security_level: SecurityLevel
):
    # Get a space with low security
    low_security_space: Space = next(
        s
        for s in base_environment.spaces
        if s.security_level_id is not None
        and s.security_level_id != high_security_level.id
    )

    # Create new space with higher security
    high_security_space = Space(
        id=low_security_space.id,
        name=low_security_space.name,
        security_level_id=high_security_level.id,
    )

    new_environment = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces - {low_security_space} | {high_security_space},
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models,
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=new_environment,
    )

    changes = env_update.get_changes()
    space_changes = [
        c for c in changes.changed_spaces if c.space.id == high_security_space.id
    ]
    assert len(space_changes) == 1
    space_change = space_changes[0]

    # Verify that the security level changed
    assert space_change.old_security_level_id == low_security_space.security_level_id
    assert space_change.new_security_level_id == high_security_level.id

    # Verify that model availability changed
    assert space_change.model_availability_changed()

    # Get models that should be removed due to insufficient security level
    low_security_models = {
        m
        for m in base_environment.completion_models
        if m.security_level_id is not None
        and m.security_level_id == low_security_space.security_level_id
    }

    # Verify that low security models are removed
    assert all(m in space_change.removed_completion_models for m in low_security_models)

    # Verify that high security models are not removed
    high_security_models = {
        m
        for m in base_environment.completion_models
        if m.security_level_id == high_security_level.id
    }
    assert not any(
        m in space_change.removed_completion_models for m in high_security_models
    )


def test_environment_rejects_duplicate_security_level_ids():
    # Create two security levels with the same ID
    duplicate_id = uuid4()
    security_levels = {
        SecurityLevel(id=duplicate_id, name="Level 1", value=1),
        SecurityLevel(id=duplicate_id, name="Level 2", value=2),
    }

    with pytest.raises(ValidationError, match="Duplicate security level IDs found"):
        Environment(
            security_levels=security_levels,
            spaces=set(),
            completion_models=set(),
            embedding_models=set(),
        )


def test_environment_rejects_duplicate_space_ids():
    # Create two spaces with the same ID
    duplicate_id = uuid4()
    spaces = {
        Space(id=duplicate_id, name="Space 1", security_level_id=None),
        Space(id=duplicate_id, name="Space 2", security_level_id=None),
    }

    with pytest.raises(ValidationError, match="Duplicate space IDs found"):
        Environment(
            security_levels=set(),
            spaces=spaces,
            completion_models=set(),
            embedding_models=set(),
        )


def test_environment_rejects_duplicate_completion_model_ids():
    # Create two completion models with the same ID
    duplicate_id = uuid4()
    completion_models = {
        CompletionModel(id=duplicate_id, name="Model 1", security_level_id=None),
        CompletionModel(id=duplicate_id, name="Model 2", security_level_id=None),
    }

    with pytest.raises(ValidationError, match="Duplicate completion model IDs found"):
        Environment(
            security_levels=set(),
            spaces=set(),
            completion_models=completion_models,
            embedding_models=set(),
        )


def test_environment_rejects_duplicate_embedding_model_ids():
    # Create two embedding models with the same ID
    duplicate_id = uuid4()
    embedding_models = {
        EmbeddingModel(id=duplicate_id, name="Model 1", security_level_id=None),
        EmbeddingModel(id=duplicate_id, name="Model 2", security_level_id=None),
    }

    with pytest.raises(ValidationError, match="Duplicate embedding model IDs found"):
        Environment(
            security_levels=set(),
            spaces=set(),
            completion_models=set(),
            embedding_models=embedding_models,
        )


def test_environment_update_embedding_model_changes(
    base_environment: Environment, high_security_level: SecurityLevel
):
    # Modify security level of an embedding model
    old_model: EmbeddingModel = next(
        m for m in base_environment.embedding_models
        if m.security_level_id != high_security_level.id
    )
    new_model = EmbeddingModel(
        id=old_model.id,
        name=old_model.name,
        security_level_id=high_security_level.id,
    )

    new_environment = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces,
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models - {old_model} | {new_model},
    )

    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=new_environment,
    )

    changes = env_update.get_changes()

    # Verify embedding model changes are tracked
    assert len(changes.changed_embedding_models) == 1
    changed_model: EmbeddingModelChange = next(iter(changes.changed_embedding_models))
    assert changed_model.embedding_model == new_model
    assert changed_model.old_security_level_id == old_model.security_level_id
    assert changed_model.new_security_level_id == high_security_level.id

    # Verify that this change affects space model availability
    space_changes = [
        c for c in changes.changed_spaces
        if old_model in c.removed_embedding_models
        and new_model in c.added_embedding_models
    ]
    assert len(space_changes) > 0
    for space_change in space_changes:
        assert space_change.model_availability_changed()


def test_embedding_model_security_level_transitions(base_environment: Environment):
    # Test various security level transitions for embedding models
    
    # Get a model with high security level to ensure there's a lower level available
    restricted_model: EmbeddingModel = next(
        m for m in base_environment.embedding_models
        if m.security_level_id is not None
        and next(
            sl.value for sl in base_environment.security_levels
            if sl.id == m.security_level_id
        ) > min(sl.value for sl in base_environment.security_levels)
    )
    
    # Test transition to unrestricted
    unrestricted_model = EmbeddingModel(
        id=restricted_model.id,
        name=restricted_model.name,
        security_level_id=None,
    )
    
    new_environment = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces,
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models - {restricted_model} | {unrestricted_model},
    )
    
    env_update = EnvironmentUpdate(
        old_environment=base_environment,
        new_environment=new_environment,
    )
    
    changes = env_update.get_changes()
    assert len(changes.changed_embedding_models) == 1
    model_change = next(iter(changes.changed_embedding_models))
    assert model_change.old_security_level_id is not None
    assert model_change.new_security_level_id is None
    
    # Test removal of security level
    model_security_level = next(
        sl for sl in base_environment.security_levels
        if sl.id == restricted_model.security_level_id
    )
    
    # Find a security level with a lower value
    lower_security_level = next(
        sl for sl in base_environment.security_levels
        if sl.value < model_security_level.value
    )
    
    # Create a space with the lower security level
    # This ensures the model is allowed in the space (since model level > space level)
    space_with_lower_level = Space(
        id=uuid4(),
        name="Test Space",
        security_level_id=lower_security_level.id,
    )
    
    base_environment_with_space = Environment(
        security_levels=base_environment.security_levels,
        spaces=base_environment.spaces | {space_with_lower_level},
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models,
    )
    
    # Now remove the model's security level
    new_environment = Environment(
        security_levels=base_environment.security_levels - {model_security_level},
        spaces=base_environment_with_space.spaces,
        completion_models=base_environment.completion_models,
        embedding_models=base_environment.embedding_models,
    )
    
    env_update = EnvironmentUpdate(
        old_environment=base_environment_with_space,
        new_environment=new_environment,
    )
    
    changes = env_update.get_changes()
    assert model_security_level in changes.removed_security_levels
    
    # Verify that the space is affected by the security level removal
    space_changes = [c for c in changes.changed_spaces if c.space.id == space_with_lower_level.id]
    assert len(space_changes) == 1
    
    space_change = space_changes[0]
    assert space_change.old_security_level_id == lower_security_level.id
    assert space_change.new_security_level_id == lower_security_level.id  # Space level doesn't change
    assert restricted_model in space_change.removed_embedding_models  # Model is removed because its security level was removed
