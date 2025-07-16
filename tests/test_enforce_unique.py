import itertools
from collections.abc import Generator
from typing import Annotated, Any

import pytest

from py_enforce import ValidationError, enforce
from py_enforce.validators import Unique

# --- Test Functions ---


@enforce
def process_collection(items: Annotated[list, Unique()]):
    """Function for testing list/collection validation."""
    return True


@enforce
def process_string(text: Annotated[str, Unique()]):
    """Function for testing string validation."""
    return True


@enforce
def invalid_validator_usage(data: Annotated[int, Unique()]):
    """Function where Unique is used on an invalid type (non-iterable)."""
    return True


# --- Test Cases ---


def test_unique_list_success():
    """Tests that a list of unique items passes validation."""
    assert process_collection([1, 2, 3, "a", None])


def test_unique_tuple_success():
    """Tests that a tuple of unique items passes validation."""
    # Note: The type hint is list, but validation happens at runtime.
    # This tests that the validator works on tuple values.
    assert process_collection(("a", "b", "c"))


def test_unique_string_success():
    """Tests that a string with unique characters passes validation."""
    assert process_string("abcdef")


def test_empty_collection_is_unique():
    """Tests that an empty list is considered unique."""
    assert process_collection([])


def test_single_item_collection_is_unique():
    """Tests that a single-item list is considered unique."""
    assert process_collection([100])


def test_set_is_always_unique():
    """Tests that a set, which is inherently unique, passes."""
    assert process_collection({1, 2, 3})


def test_duplicate_integers_fail():
    """Tests that a list with duplicate integers raises a ValidationError."""
    with pytest.raises(
        ValidationError, match="Parameter 'items' must contain unique elements."
    ):
        process_collection([1, 2, 1])


def test_duplicate_strings_fail():
    """Tests that a list with duplicate strings raises a ValidationError."""
    with pytest.raises(
        ValidationError, match="Parameter 'items' must contain unique elements."
    ):
        process_collection(["hello", "world", "hello"])


def test_duplicate_nones_fail():
    """Tests that a list with duplicate None values raises a ValidationError."""
    with pytest.raises(
        ValidationError, match="Parameter 'items' must contain unique elements."
    ):
        process_collection([1, None, 2, None])


def test_duplicate_string_characters_fail():
    """Tests that a string with duplicate characters raises a ValidationError."""
    with pytest.raises(
        ValidationError, match="Parameter 'text' must contain unique elements."
    ):
        process_string("hello world")


def test_equality_across_types_fail():
    """
    Tests for values that are different types but considered equal (e.g., 1 == 1.0).
    A set treats these as the same element.
    """
    with pytest.raises(
        ValidationError, match="Parameter 'items' must contain unique elements."
    ):
        process_collection([1, True, 1.0])  # set({1, True, 1.0}) -> {1}


def test_unhashable_items_raises_type_error():
    """
    Tests that a list containing unhashable items (like lists or dicts)
    raises a TypeError when the validator tries to create a set.
    """
    with pytest.raises(TypeError, match="unhashable type"):
        process_collection([1, [2, 3], 4])

    with pytest.raises(TypeError, match="unhashable type"):
        process_collection([1, {"a": 1}, 4])


def test_validator_on_non_collection_type():
    """
    Tests that using the Unique validator on a non-iterable type raises a TypeError.
    """
    expected_error_msg = (
        "Validator 'Unique' can only be used on types that are iterable "
        "and contain hashable elements"
    )
    with pytest.raises(TypeError, match=expected_error_msg):
        invalid_validator_usage(123)


# --- Generator Test Functions ---


@enforce
def process_generator[T](items: Annotated[Generator[T], Unique()]) -> list[T]:
    """A function that consumes a generator"""
    return list(items)


@enforce
def process_eagerly_for_uniqueness[T](
    items: Annotated[list[T], Unique(exhaust_generators=True)],
) -> list[T]:
    """
    A test function that uses Unique in eager mode.
    The validator should consume the generator before the function body runs.
    """
    return items


# --- Generator Test Cases ---


def test_unique_generator_success():
    """
    Tests that a generator with unique elements passes validation and is not consumed.
    """

    def my_generator():
        yield 1
        yield 2
        yield 3

    gen = my_generator()
    # The function should successfully process the generator and return all items
    result = process_generator(gen)
    assert result == [1, 2, 3]


def test_unique_generator_fail_early():
    """Tests that a generator with early duplicates fails quickly without consuming the entire generator."""  # noqa: E501

    def early_duplicate_generator():
        yield 1
        yield 1  # duplicate appears early
        yield 2
        yield 3

    gen = early_duplicate_generator()
    with pytest.raises(
        ValidationError, match="Parameter 'items' must contain unique elements."
    ):
        process_generator(gen)


def test_unique_generator_fail_late():
    """Tests that a generator with late duplicates eventually fails."""

    def late_duplicate_generator():
        yield from range(-1_000, 1_000)
        yield 2  # duplicate appears late

    gen = late_duplicate_generator()
    with pytest.raises(
        ValidationError, match="Parameter 'items' must contain unique elements."
    ):
        process_generator(gen)


def test_unique_empty_generator_success():
    """Tests that an empty generator passes validation (empty is unique)."""

    def empty_generator():
        yield from []

    gen = empty_generator()
    result = process_generator(gen)
    assert result == []


def test_unique_single_item_generator_success():
    """Tests that a single-item generator passes validation."""

    def single_generator():
        yield 42

    gen = single_generator()
    result = process_generator(gen)
    assert result == [42]


def test_unique_infinite_generator_success():
    """
    Tests that an infinite generator with unique elements works and is not exhausted by validation.
    The validation happens lazily and must not hang.
    """  # noqa: E501

    def infinite_unique_generator():
        yield from itertools.count()  # 0, 1, 2, 3, 4, ...

    gen = infinite_unique_generator()

    @enforce
    def process_items_for_uniqueness(items: Annotated[Any, Unique()]):
        return items

    # This call should return immediately without hanging.
    validated_gen = process_items_for_uniqueness(gen)

    assert [next(validated_gen) for _ in range(1_000)] == list(range(1_000))


def test_unique_infinite_generator_fail():
    """Tests that an infinite generator with duplicates fails when the duplicate is encountered."""  # noqa: E501

    def infinite_duplicate_generator():
        yield 50
        yield from itertools.count()

    gen = infinite_duplicate_generator()

    @enforce
    def process_items_for_uniqueness(items: Annotated[Any, Unique()]):
        return list(items)  # Will hang if Unique does not kick in

    with pytest.raises(
        ValidationError, match="Parameter 'items' must contain unique elements."
    ):
        process_items_for_uniqueness(gen)


def test_unique_generator_eager_success():
    """Tests that a generator with unique elements passes eager validation but is fully consumed."""  # noqa: E501

    def my_generator():
        yield from range(-1_000, 1_000)

    gen = my_generator()

    # The validation happens on call and should succeed.
    # The validator consumes the generator as per the flag and should return a list.
    result = process_eagerly_for_uniqueness(gen)

    assert result == list(range(-1_000, 1_000))


def test_unique_generator_eager_fail():
    """Tests that a generator with duplicate elements fails eager validation on call."""

    def duplicate_generator():
        yield 1
        yield 2
        yield 1  # duplicate

    gen = duplicate_generator()
    with pytest.raises(
        ValidationError, match="Parameter 'items' must contain unique elements."
    ):
        process_eagerly_for_uniqueness(gen)


def test_unique_generator_eager_empty_success():
    """
    Tests that an empty generator passes eager validation.
    """

    def empty_generator():
        yield from []

    gen = empty_generator()
    result = process_eagerly_for_uniqueness(gen)
    assert result == []


def test_unique_generator_with_unhashable_elements():
    """Tests that a generator containing unhashable elements raises a TypeError."""

    def unhashable_generator():
        yield 1
        yield [2, 3]  # unhashable list
        yield 4

    gen = unhashable_generator()
    with pytest.raises(TypeError, match="unhashable type"):
        process_generator(gen)


@pytest.mark.skip(
    "This test is expected to hang and is for documentation purposes only."
    "The `exhaust_generators=True` policy forces full consumption."
)
def test_unique_generator_eager_infinite_hangs():
    """
    This test documents the expected (and dangerous) behavior of eager validation
    on an infinite generator. The `exhaust_generators=True` policy forces full consumption.
    """  # noqa: E501

    def infinite_generator():
        yield from itertools.count()

    gen = infinite_generator()
    # This call will never return as it tries to iterate an infinite stream.
    process_eagerly_for_uniqueness(gen)
