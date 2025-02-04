from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel
import pytest
from typing import TypeVar, Generic, Type
from instorage.securitylevels.security_level_analysis import (
    SecurityLevel,
    Space,
    CompletionModel,
    EmbeddingModel,
    SpaceChange,
    Environment,
    EnvironmentUpdate,
    EnvironmentChange,
)
from pydantic import ValidationError

# Test UUIDs for consistent testing
TEST_IDS = {
    "low_level": UUID("11111111-1111-1111-1111-111111111111"),
    "medium_level": UUID("22222222-2222-2222-2222-222222222222"),
    "high_level": UUID("33333333-3333-3333-3333-333333333333"),
    "space_1": UUID("44444444-4444-4444-4444-444444444444"),
    "space_2": UUID("55555555-5555-5555-5555-555555555555"),
    "completion_1": UUID("66666666-6666-6666-6666-666666666666"),
    "completion_2": UUID("77777777-7777-7777-7777-777777777777"),
    "embedding_1": UUID("88888888-8888-8888-8888-888888888888"),
    "embedding_2": UUID("99999999-9999-9999-9999-999999999999"),
}


class SecurityLevelSpec(BaseModel):
    value: int | None
    display_name: str


LOW = SecurityLevelSpec(value=10, display_name="Low")
MEDIUM = SecurityLevelSpec(value=50, display_name="Medium")
HIGH = SecurityLevelSpec(value=100, display_name="High")


T = TypeVar("T", Space, EmbeddingModel, CompletionModel)


class Mutator(BaseModel, Generic[T], frozen=True):
    base: T
    base_spec: SecurityLevelSpec

    @classmethod
    def from_spec(cls, model_class: Type[T], spec: SecurityLevelSpec) -> "Mutator[T]":
        if model_class is Space:
            return cls(
                base=Space(
                    id=uuid4(),
                    name=f"{spec.display_name} Space",
                    security_level_id=None,
                ),
                base_spec=spec,
            )
        elif model_class is EmbeddingModel:
            return cls(
                base=EmbeddingModel(
                    id=uuid4(),
                    name=f"{spec.display_name} Embedding Model",
                    security_level_id=None,
                ),
                base_spec=spec,
            )
        elif model_class is CompletionModel:
            return cls(
                base=CompletionModel(
                    id=uuid4(),
                    name=f"{spec.display_name} Completion Model",
                    security_level_id=None,
                ),
                base_spec=spec,
            )
        raise ValueError(f"Unsupported model class: {model_class}")


@pytest.fixture
def security_levels():
    """Create a set of security levels for testing."""
    return {
        "low": SecurityLevel(id=TEST_IDS["low_level"], name="low", value=10),
        "medium": SecurityLevel(id=TEST_IDS["medium_level"], name="medium", value=50),
        "high": SecurityLevel(id=TEST_IDS["high_level"], name="high", value=100),
    }


@pytest.fixture
def spaces():
    """Create a set of spaces for testing."""
    return {
        "no_security": Space(
            id=TEST_IDS["space_1"], name="no_security_space", security_level_id=None
        ),
        "low_security": Space(
            id=TEST_IDS["space_2"],
            name="low_security_space",
            security_level_id=TEST_IDS["low_level"],
        ),
    }


@pytest.fixture
def completion_models():
    """Create a set of completion models for testing."""
    return {
        "no_security": CompletionModel(
            id=TEST_IDS["completion_1"],
            name="no_security_completion",
            security_level_id=None,
        ),
        "low_security": CompletionModel(
            id=TEST_IDS["completion_2"],
            name="low_security_completion",
            security_level_id=TEST_IDS["low_level"],
        ),
    }


@pytest.fixture
def embedding_models():
    """Create a set of embedding models for testing."""
    return {
        "no_security": EmbeddingModel(
            id=TEST_IDS["embedding_1"],
            name="no_security_embedding",
            security_level_id=None,
        ),
        "low_security": EmbeddingModel(
            id=TEST_IDS["embedding_2"],
            name="low_security_embedding",
            security_level_id=TEST_IDS["low_level"],
        ),
    }


@pytest.fixture
def base_environment(security_levels, spaces, completion_models, embedding_models):
    """Create a base environment for testing."""
    return Environment(
        security_levels=set(security_levels.values()),
        spaces=set(spaces.values()),
        completion_models=set(completion_models.values()),
        embedding_models=set(embedding_models.values()),
    )


# Test cases for environment mutations
def mutate_security_level_value(
    env: Environment, level_id: UUID, new_value: int
) -> Environment:
    """Mutate a security level's value in the environment."""
    new_levels = {
        sl.model_copy(update={"value": new_value}) if sl.id == level_id else sl
        for sl in env.security_levels
    }
    return env.model_copy(update={"security_levels": set(new_levels)})


def mutate_space_security_level(
    env: Environment, space_id: UUID, new_level_id: UUID | None
) -> Environment:
    """Mutate a space's security level in the environment."""
    new_spaces = {
        s.model_copy(update={"security_level_id": new_level_id})
        if s.id == space_id
        else s
        for s in env.spaces
    }
    return env.model_copy(update={"spaces": set(new_spaces)})


def mutate_completion_model_security_level(
    env: Environment, model_id: UUID, new_level_id: UUID | None
) -> Environment:
    """Mutate a completion model's security level in the environment."""
    new_models = {
        m.model_copy(update={"security_level_id": new_level_id})
        if m.id == model_id
        else m
        for m in env.completion_models
    }
    return env.model_copy(update={"completion_models": set(new_models)})


def mutate_embedding_model_security_level(
    env: Environment, model_id: UUID, new_level_id: UUID | None
) -> Environment:
    """Mutate an embedding model's security level in the environment."""
    new_models = {
        m.model_copy(update={"security_level_id": new_level_id})
        if m.id == model_id
        else m
        for m in env.embedding_models
    }
    return env.model_copy(update={"embedding_models": set(new_models)})


# Parameterized test cases
@pytest.mark.parametrize(
    "mutation_scenario",
    [
        # Security level value changes
        pytest.param(
            {
                "name": "increase_low_level_value",
                "mutation": lambda env: mutate_security_level_value(
                    env, TEST_IDS["low_level"], 20
                ),
                "expected_changes": 1,
            },
            id="increase_low_security_level_value",
        ),
        pytest.param(
            {
                "name": "decrease_high_level_value",
                "mutation": lambda env: mutate_security_level_value(
                    env, TEST_IDS["high_level"], 40
                ),
                "expected_changes": 0,  # No changes expected as no spaces use high level
            },
            id="decrease_high_security_level_value",
        ),
        # Space security level changes
        pytest.param(
            {
                "name": "add_security_to_unsecure_space",
                "mutation": lambda env: mutate_space_security_level(
                    env, TEST_IDS["space_1"], TEST_IDS["low_level"]
                ),
                "expected_changes": 1,
            },
            id="add_security_to_unsecure_space",
        ),
        pytest.param(
            {
                "name": "remove_security_from_secure_space",
                "mutation": lambda env: mutate_space_security_level(
                    env, TEST_IDS["space_2"], None
                ),
                "expected_changes": 1,
            },
            id="remove_security_from_secure_space",
        ),
        pytest.param(
            {
                "name": "increase_space_security_level",
                "mutation": lambda env: mutate_space_security_level(
                    env, TEST_IDS["space_2"], TEST_IDS["medium_level"]
                ),
                "expected_changes": 1,
            },
            id="increase_space_security_level",
        ),
        # Completion model security level changes
        pytest.param(
            {
                "name": "add_security_to_unsecure_completion_model",
                "mutation": lambda env: mutate_completion_model_security_level(
                    env, TEST_IDS["completion_1"], TEST_IDS["low_level"]
                ),
                "expected_changes": 2,  # Changes in both spaces
            },
            id="add_security_to_unsecure_completion_model",
        ),
        pytest.param(
            {
                "name": "remove_security_from_secure_completion_model",
                "mutation": lambda env: mutate_completion_model_security_level(
                    env, TEST_IDS["completion_2"], None
                ),
                "expected_changes": 1,  # Changes only in the secure space
            },
            id="remove_security_from_secure_completion_model",
        ),
        pytest.param(
            {
                "name": "increase_completion_model_security",
                "mutation": lambda env: mutate_completion_model_security_level(
                    env, TEST_IDS["completion_2"], TEST_IDS["medium_level"]
                ),
                "expected_changes": 1,  # Changes in the low security space
            },
            id="increase_completion_model_security",
        ),
        # Embedding model security level changes
        pytest.param(
            {
                "name": "add_security_to_unsecure_embedding_model",
                "mutation": lambda env: mutate_embedding_model_security_level(
                    env, TEST_IDS["embedding_1"], TEST_IDS["low_level"]
                ),
                "expected_changes": 2,  # Changes in both spaces
            },
            id="add_security_to_unsecure_embedding_model",
        ),
        pytest.param(
            {
                "name": "remove_security_from_secure_embedding_model",
                "mutation": lambda env: mutate_embedding_model_security_level(
                    env, TEST_IDS["embedding_2"], None
                ),
                "expected_changes": 1,  # Changes only in the secure space
            },
            id="remove_security_from_secure_embedding_model",
        ),
        pytest.param(
            {
                "name": "increase_embedding_model_security",
                "mutation": lambda env: mutate_embedding_model_security_level(
                    env, TEST_IDS["embedding_2"], TEST_IDS["medium_level"]
                ),
                "expected_changes": 1,  # Changes in the low security space
            },
            id="increase_embedding_model_security",
        ),
    ],
)
def test_environment_mutations(base_environment, mutation_scenario):
    """Test various environment mutations and their effects."""
    # Apply mutation
    new_environment = mutation_scenario["mutation"](base_environment)

    # Create environment update
    update = EnvironmentUpdate(
        old_environment=base_environment, new_environment=new_environment
    )

    # Get changes
    changes = update.get_change()

    # Verify changes
    assert len(changes.changed_spaces) == mutation_scenario["expected_changes"]


def test_environment_change_details(base_environment):
    """Test the details of environment changes."""
    # Add security to an unsecure completion model
    new_environment = mutate_completion_model_security_level(
        base_environment, TEST_IDS["completion_1"], TEST_IDS["low_level"]
    )

    update = EnvironmentUpdate(
        old_environment=base_environment, new_environment=new_environment
    )

    changes = update.get_change()

    # Verify the specific changes
    assert len(changes.changed_spaces) == 2

    # Convert to list for easier access
    changed_spaces = list(changes.changed_spaces)

    # Find changes for each space
    no_security_space_change = next(
        change for change in changed_spaces if change.space.id == TEST_IDS["space_1"]
    )
    low_security_space_change = next(
        change for change in changed_spaces if change.space.id == TEST_IDS["space_2"]
    )

    # Verify changes for no security space
    assert len(no_security_space_change.removed_completion_model_ids) == 1
    assert (
        TEST_IDS["completion_1"]
        in no_security_space_change.removed_completion_model_ids
    )
    assert len(no_security_space_change.added_completion_model_ids) == 0

    # Verify changes for low security space
    assert len(low_security_space_change.removed_completion_model_ids) == 0
    assert len(low_security_space_change.added_completion_model_ids) == 1
    assert (
        TEST_IDS["completion_1"] in low_security_space_change.added_completion_model_ids
    )


def test_environment_validation():
    """Test environment validation rules."""
    # Test duplicate security level IDs
    with pytest.raises(ValidationError):
        Environment(
            security_levels={
                SecurityLevel(id=TEST_IDS["low_level"], name="low1", value=10),
                SecurityLevel(id=TEST_IDS["low_level"], name="low2", value=20),
            },
            spaces=set(),
            completion_models=set(),
            embedding_models=set(),
        )

    # Test duplicate space IDs
    with pytest.raises(ValidationError):
        Environment(
            security_levels=set(),
            spaces={
                Space(id=TEST_IDS["space_1"], name="space1", security_level_id=None),
                Space(id=TEST_IDS["space_1"], name="space2", security_level_id=None),
            },
            completion_models=set(),
            embedding_models=set(),
        )

    # Test duplicate completion model IDs
    with pytest.raises(ValidationError):
        Environment(
            security_levels=set(),
            spaces=set(),
            completion_models={
                CompletionModel(
                    id=TEST_IDS["completion_1"], name="model1", security_level_id=None
                ),
                CompletionModel(
                    id=TEST_IDS["completion_1"], name="model2", security_level_id=None
                ),
            },
            embedding_models=set(),
        )

    # Test duplicate embedding model IDs
    with pytest.raises(ValidationError):
        Environment(
            security_levels=set(),
            spaces=set(),
            completion_models=set(),
            embedding_models={
                EmbeddingModel(
                    id=TEST_IDS["embedding_1"], name="model1", security_level_id=None
                ),
                EmbeddingModel(
                    id=TEST_IDS["embedding_1"], name="model2", security_level_id=None
                ),
            },
        )
