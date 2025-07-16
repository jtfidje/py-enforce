import itertools
from typing import Annotated, Any

import pytest

from py_enforce import ValidationError, enforce
from py_enforce.validators import NotEmpty

# --- Test Functions ---


@enforce
def process_items(items: Annotated[list[int], NotEmpty()]) -> bool:
    """Function for testing list validation."""
    return True


@enforce
def greet(name: Annotated[str, NotEmpty()]) -> str:
    """Function for testing string validation."""
    return f"Hello, {name}"


@enforce
def configure_system(
    name: Annotated[str, NotEmpty()], settings: Annotated[dict, NotEmpty()]
) -> str:
    """Function for testing multiple validated arguments."""
    return f"Configuring {name} with {len(settings)} settings."


@enforce
def invalid_validator_usage(data: Annotated[int, NotEmpty()]) -> int:
    """Function where NotEmpty is used on an invalid type."""
    return data


# --- Test Cases ---


def test_not_empty_list_success():
    """Tests that a non-empty list passes validation."""
    assert process_items([1, 2, 3])


def test_not_empty_list_fail():
    """Tests that an empty list raises a ValidationError."""
    with pytest.raises(
        ValidationError,
        match="Parameter 'items' cannot be empty for function 'process_items'.",
    ):
        process_items([])


def test_not_empty_string_success():
    """Tests that a non-empty string passes validation."""
    assert greet("World") == "Hello, World"


def test_not_empty_string_fail():
    """Tests that an empty string raises a ValidationError."""
    with pytest.raises(
        ValidationError, match="Parameter 'name' cannot be empty for function 'greet'."
    ):
        greet("")


def test_multiple_validators_success():
    """Tests a function with multiple validated arguments passing."""
    result = configure_system(name="server-1", settings={"port": 8080})
    assert result == "Configuring server-1 with 1 settings."


def test_multiple_validators_fail_first():
    """Tests that the first of multiple arguments failing raises an error."""
    with pytest.raises(
        ValidationError,
        match="Parameter 'name' cannot be empty for function 'configure_system'.",
    ):
        configure_system(name="", settings={"port": 8080})


def test_multiple_validators_fail_second():
    """Tests that the second of multiple arguments failing raises an error."""
    with pytest.raises(
        ValidationError,
        match="Parameter 'settings' cannot be empty for function 'configure_system'.",
    ):
        configure_system(name="server-1", settings={})


def test_keyword_arguments():
    """Ensures validation works correctly with keyword arguments."""
    assert process_items(items=[1])
    with pytest.raises(ValidationError):
        process_items(items=[])


def test_validator_on_invalid_type():
    """
    Tests that using a validator on an incompatible type raises a TypeError.
    NotEmpty should not work on an int.
    """
    with pytest.raises(
        TypeError,
        match="Validator 'NotEmpty' can only be used on types that support len()",
    ):
        invalid_validator_usage(123)


# --- Generator Test Functions ---


@enforce
def process_generator(items: Annotated[Any, NotEmpty()]):
    """A function that consumes a generator."""
    return list(items)


@enforce
def process_eagerly_for_emptiness(
    items: Annotated[Any, NotEmpty(exhaust_generators=True)],
) -> list[Any]:
    """
    A test function that uses NotEmpty in eager mode.
    The validator should consume the generator before the function body runs.
    """
    return items


# --- Generator Test Cases ---


def test_not_empty_generator_success():
    """Tests that a non-empty generator passes validation and is not consumed."""

    def my_generator():
        yield from range(-1_000, 1_000)

    gen = my_generator()

    result = process_generator(gen)
    assert result == list(range(-1_000, 1_000))


def test_not_empty_generator_fail():
    """Tests that an empty generator raises a ValidationError."""

    def empty_generator():
        yield from []

    gen = empty_generator()
    with pytest.raises(ValidationError, match="Parameter 'items' cannot be empty."):
        process_generator(gen)


def test_not_empty_infinite_generator_success():
    """
    Tests that an infinite generator works and is not exhausted by validation.
    The validation happens on call and must not hang.
    """

    def infinite_generator():
        yield from itertools.count()  # 0, 1, 2, 3, 4, ...

    gen = infinite_generator()

    @enforce
    def process_items_for_emptiness(items: Annotated[Any, NotEmpty()]):
        return items

    # This call should return immediately without hanging.
    validated_gen = process_items_for_emptiness(gen)

    assert [next(validated_gen) for _ in range(1_000)] == list(range(1_000))


def test_not_empty_generator_eager_success():
    """Tests that a non-empty generator passes eager validation but is fully consumed."""

    def my_generator():
        yield from range(-1_000, 1_000)

    gen = my_generator()
    result = process_eagerly_for_emptiness(gen)

    assert result == list(range(-1_000, 1_000))


def test_not_empty_generator_eager_fail():
    """Tests that an empty generator fails eager validation on call."""

    def empty_generator():
        yield from []

    gen = empty_generator()
    with pytest.raises(ValidationError, match="Parameter 'items' cannot be empty."):
        process_eagerly_for_emptiness(gen)


@pytest.mark.skip(
    "This test is expected to hang and is for documentation purposes only."
    "The `exhaust_generators=True` policy forces full consumption."
)
def test_not_empty_generator_eager_infinite_hangs():
    """
    This test documents the expected (and dangerous) behavior of eager validation
    on an infinite generator. Even though NotEmpty could pass after one item,
    the `exhaust_generators=True` policy forces full consumption.
    """

    def infinite_generator():
        yield from itertools.count()

    gen = infinite_generator()
    # This call will never return as it tries to iterate an infinite stream.
    process_eagerly_for_emptiness(gen)
