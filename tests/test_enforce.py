from collections.abc import Generator
from typing import Annotated, Any

import pytest

from py_enforce import ValidationError, enforce
from py_enforce.validators import NotEmpty
from py_enforce.validators.bases import Validator


def test_function_with_no_annotations():
    """Ensures the decorator doesn't interfere with un-annotated functions."""

    @enforce
    def no_annotations(value: int):
        """Function with no validation to ensure it's unaffected."""
        return value * 2

    assert no_annotations(10) == 20


def test_function_with_mixed_annotations():
    """Tests that only annotated arguments are validated."""

    @enforce
    def mixed_annotations(
        required: Annotated[str, NotEmpty()], optional: str = "default"
    ):
        """Function with mixed annotated and non-annotated arguments."""
        return f"{required} and {optional}"

    assert mixed_annotations("required_val") == "required_val and default"

    with pytest.raises(ValidationError):
        mixed_annotations("")


def test_function_with_missing_type_annotation():
    """Tests that the decorator doesn't interfere with missing type annotations."""

    @enforce
    def empty_annotation(value):
        return value

    assert empty_annotation(10) == 10


def test_function_with_non_validator_annotation():
    """Test that the decorator doesn't interfere with non-validator annotations"""

    @enforce
    def non_validator_annotation(value: Annotated[int, ...]) -> int:
        return value

    assert non_validator_annotation(10) == 10


def test_function_with_generator_incompatible_validator():
    """
    Test that the decorator raises an exception is a generator is passed to a validator
    that does not support generator validation
    """

    class NonGeneratorValidator(Validator):
        def validate(self, *args, **kwargs) -> None: ...

    @enforce
    def some_function(data: Annotated[Generator[Any], NonGeneratorValidator()]): ...

    with pytest.raises(
        TypeError, match="Parameter 'data' for function 'some_function' is a generator"
    ):
        some_function(data=(i for i in range(10)))
