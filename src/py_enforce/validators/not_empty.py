from collections.abc import Generator, Sized

from ..exceptions import ValidationError
from .bases import GeneratorValidator


class NotEmpty(GeneratorValidator):
    """
    Validator to ensure a collection or string is not empty.

    This validator can be used with any type that supports the `len()` function
    (i.e., conforms to collections.abc.Sized).
    """

    def validate(self, value: Sized, func_name: str, param_name: str) -> None:
        """
        Checks if the value is not empty.

        Args:
            value (collections.abc.Sized): The value to check. Must be of a type that implements __len__.
            func_name (str): The name of the function being validated.
            param_name (str): The name of the parameter being validated.

        Raises:
            ValidationError: If the value is empty.
            TypeError: If the value is not of type collections.abc.Sized.
        """  # noqa: E501
        if not isinstance(value, Sized):
            raise TypeError(
                "Validator 'NotEmpty' can only be used on types that support len() "
                f"(collections.abc.Sized), but function '{func_name}' "
                f"got type '{type(value).__name__}' for parameter '{param_name}'."
            )

        if len(value) == 0:
            raise ValidationError(
                f"Parameter '{param_name}' cannot be empty for function '{func_name}'."
            )

    def wrap_generator[T](
        self, value: Generator[T], func_name: str, param_name: str
    ) -> Generator[T]:
        """
        Wraps a generator with lazy validation logic to ensure it's not empty.

        Args:
            value (collections.abc.Generator): The generator to wrap and validate.
            func_name (str): The name of the function being validated.
            param_name (str): The name of the parameter being validated.

        Returns:
            Generator[T]: A wrapped generator that validates non-emptiness on first access.

        Raises:
            ValidationError: If the generator is empty (produces no values).
        """  # noqa: E501

        def wrapper(gen: Generator[T]) -> Generator[T]:
            # Try to fetch the first value from the generator
            try:
                val = next(gen)
            except StopIteration:
                raise ValidationError(
                    f"Parameter '{param_name}' cannot be empty for function '{func_name}'."  # noqa: E501
                )
            else:
                yield val

            # No more validation needed
            yield from gen

        return wrapper(value)
