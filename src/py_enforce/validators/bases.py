import abc
from typing import Any, Generator


class Validator(abc.ABC):
    """Base class for all validators."""

    @abc.abstractmethod
    def validate(self, value: Any, func_name: str, param_name: str) -> None:
        """
        Performs validation on the given value.

        Args:
            value (Any): The value of the argument to validate.
            func_name (str): The name of the function being validated.
            param_name (str): The name of the parameter being validated.

        Raises:
            ValidationError: If validation fails.
            TypeError: If a validator is used on an incompatible type
        """
        ...


class GeneratorValidator(Validator):
    """Base class for all validators that support handling generators"""

    def __init__(self, exhaust_generators: bool = False) -> None:
        super().__init__()
        self.exhaust_generators = exhaust_generators

    @abc.abstractmethod
    def wrap_generator[T](
        self, value: Generator[T], func_name: str, param_name: str
    ) -> Generator[T]:
        """
        Wraps a generator with lazy validation logic, performing on-the-fly validation.

        Args:
            value (collections.abc.Generator): The generator to wrap.
            func_name (str): The name of the function being validated.
            param_name (str): The name of the parameter being validated.

        Raises:
            ValidationError: If validation fails
        """
        ...
