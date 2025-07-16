import functools
import inspect
import typing
from collections.abc import Callable, Generator
from typing import Any

from .validators.bases import GeneratorValidator, Validator


def enforce(func: Callable) -> Callable:
    """
    A decorator that enforces validation rules defined in `Annotated` type hints.
    """
    sig = inspect.signature(func)

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Bind the passed arguments to the function's signature to get a mapping
        # of parameter names to their values.
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param in sig.parameters.items():
            if param.annotation is param.empty:
                continue

            if typing.get_origin(param.annotation) is not typing.Annotated:
                continue

            _, *validators = typing.get_args(param.annotation)
            argument_value = bound_args.arguments[param_name]

            for validator in validators:
                if not isinstance(validator, Validator):
                    continue

                if isinstance(argument_value, Generator):
                    if not isinstance(validator, GeneratorValidator):
                        raise TypeError(
                            f"Parameter '{param_name}' for function '{func.__name__}' is a generator, but "  # noqa: E501
                            f"validator '{validator.__class__.__name__}' does not support validation of generators"  # noqa: E501
                        )

                    if validator.exhaust_generators:
                        argument_value = list(argument_value)
                        bound_args.arguments[param_name] = argument_value
                    else:
                        bound_args.arguments[param_name] = validator.wrap_generator(
                            argument_value,
                            func_name=func.__name__,
                            param_name=param_name,
                        )
                        continue

                validator.validate(
                    value=argument_value,
                    func_name=func.__name__,
                    param_name=param_name,
                )

        return func(*bound_args.args, **bound_args.kwargs)

    return wrapper
