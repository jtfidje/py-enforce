from collections.abc import Collection, Generator

from ..exceptions import ValidationError
from .bases import GeneratorValidator


class Unique(GeneratorValidator):
    """
    Validator to ensure a collection is unique

    This validator can be used with any sized, iterable container with hashable elements
    (i.e. conforms to the collections.abc.Collection).
    """

    def validate(self, value: Collection, func_name: str, param_name: str) -> None:
        """
        Checks if value contains only unique elements.

        Args:
            value (collections.abc.Collection): The value to check. Must be a sized, iterable container.
            func_name (str): The name of the function being validated.
            param_name (str): The name of the parameter being validated.

        Raises:
            ValidationError: If validation fails.
            TypeError: If the value is not of type collections.abc.Collection
        """  # noqa: E501
        if not isinstance(value, Collection):
            raise TypeError(
                "Validator 'Unique' can only be used on types that are iterable and "
                f"contain hashable elements (Collection), but function '{func_name}' "
                f"got type '{type(value).__name__}' for paramter '{param_name}'"
            )

        if isinstance(value, set):
            return

        if len(value) != len(set(value)):
            raise ValidationError(
                f"Parameter '{param_name}' must contain unique elements "
                f"for function {func_name}"
            )

    def wrap_generator[T](
        self, value: Generator[T], func_name: str, param_name: str
    ) -> Generator[T]:
        """
        Wraps a generator with lazy validation logic to ensure unique elements.

        Args:
            value (collections.abc.Generator): The generator to wrap.
            func_name (str): The name of the function being validated.
            param_name (str): The name of the parameter being validated.

        Returns:
            Generator[T]: A wrapped generator that validates uniqueness on-the-fly.

        Raises:
            ValidationError: If duplicate elements are encountered.
        """

        def wrapper(gen: Generator[T]) -> Generator[T]:
            seen = set()
            for val in gen:
                if val in seen:
                    raise ValidationError(
                        f"Parameter '{param_name}' must contain unique elements "
                        f"for function {func_name}"
                    )

                yield val
                seen.add(val)

        return wrapper(value)
