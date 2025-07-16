from typing import Annotated

import pytest

from py_enforce import ValidationError, enforce
from py_enforce.validators import NotEmpty


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
