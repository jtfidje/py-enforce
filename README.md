# py-enforce

A lightweight Python library for runtime validation of function parameters using type annotations

## Features

- **Type-safe validation**: Leverage Python's type annotations with `Annotated` types for parameter validation
- **Decorator-based**: Simple `@enforce` decorator that integrates seamlessly with existing code
- **Extensible**: Easy to create custom validators by extending the base `Validator` class
- **Zero dependencies**: Pure Python implementation with no external dependencies

## Installation

Since this package is not yet published to PyPI, you can install it directly from GitHub using `uv`:

```bash
uv add git+https://github.com/jtfidje/py-enforce.git
```

Or if you prefer pip:

```bash
pip install git+https://github.com/jtfidje/py-enforce.git
```

## Quick Start

```python
from typing import Annotated
from py_enforce import enforce, ValidationError
from py_enforce.validators import NotEmpty, Unique

@enforce
def greet(name: Annotated[str, NotEmpty()]) -> str:
    return f"Hello, {name}!"

@enforce
def process_items(items: Annotated[list[int], NotEmpty(), Unique()]) -> list[int]:
    return [x * 2 for x in items]

# Valid usage
print(greet("Alice"))  # "Hello, Alice!"
print(process_items([1, 2, 3]))  # [2, 4, 6]

# Invalid usage - raises ValidationError
try:
    greet("")  # Empty string
except ValidationError as e:
    print(e)  # Parameter 'name' cannot be empty for function 'greet'.

try:
    process_items([1, 2, 2])  # Duplicate values
except ValidationError as e:
    print(e)  # Parameter 'items' must contain unique elements for function process_items
```

## Built-in Validators

### NotEmpty

Ensures that collections, strings, or other sized objects are not empty.

```python
from typing import Annotated
from py_enforce import enforce
from py_enforce.validators import NotEmpty

@enforce
def process_list(items: Annotated[list, NotEmpty()]):
    return len(items)

@enforce
def process_string(text: Annotated[str, NotEmpty()]):
    return text.upper()

# Works with any type that implements __len__
@enforce
def process_dict(data: Annotated[dict, NotEmpty()]):
    return list(data.keys())
```

### Unique

Ensures that collections contain only unique elements.

```python
from typing import Annotated
from py_enforce import enforce
from py_enforce.validators import Unique

@enforce
def process_unique_items(items: Annotated[list[int], Unique()]):
    return sum(items)

@enforce
def get_unique_names(names: Annotated[list[str], Unique()]):
    return sorted(names)
```

## Generator Support

py-enforce provides support for generator validation with two modes:

### Lazy Validation (Default)

Validators wrap generators and validate elements on-the-fly without consuming the entire generator:

```python
from typing import Annotated, Generator
from py_enforce import enforce
from py_enforce.validators import NotEmpty

@enforce
def process_stream(data: Annotated[Generator[int, None, None], NotEmpty()]):
    return sum(data)

def number_generator():
    yield from range(1, 1_000_000)  # Large generator

# The generator is not fully consumed during validation
result = process_stream(number_generator())
```

### Eager Validation

Force validators to consume generators completely before function execution:

```python
from typing import Annotated, Generator
from py_enforce import enforce
from py_enforce.validators import NotEmpty, Unique

@enforce
def process_eagerly(
    data: Annotated[Generator[int, None, None], NotEmpty(exhaust_generators=True)]
):
    return data  # Now a list, not a generator

def small_generator():
    yield from [1, 2, 3, 4, 5]

# Generator is fully consumed and converted to list
result = process_eagerly(small_generator())
print(type(result))  # <class 'list'>
```

## Creating Custom Validators

Extend the base `Validator` class to create custom validation logic:

```python
from py_enforce.validators.bases import Validator
from py_enforce.exceptions import ValidationError

class MinLength(Validator):
    def __init__(self, min_length: int):
        super().__init__()
        self.min_length = min_length

    def validate(self, value, func_name: str, param_name: str) -> None:
        if len(value) < self.min_length:
            raise ValidationError(
                f"Parameter '{param_name}' must have at least {self.min_length} "
                f"characters for function '{func_name}'"
            )

# Usage
@enforce
def create_user(username: Annotated[str, MinLength(3)]):
    return f"User: {username}"
```

For generators, extend `GeneratorValidator`:

```python
from collections.abc import Generator
from py_enforce.validators.bases import GeneratorValidator
from py_enforce.exceptions import ValidationError

class MinSum(GeneratorValidator):
    def __init__(self, min_sum: int):
        self.min_sum = min_sum

    def validate(self, value, func_name: str, param_name: str) -> None:
        if sum(value) < self.min_sum:
            raise ValidationError(
                f"Parameter '{param_name}' sum must be at least {self.min_sum}"
            )

    def wrap_generator(self, value: Generator, func_name: str, param_name: str) -> Generator:
        def wrapper(gen):
            total = 0
            for item in gen:
                total += item
                yield item
            if total < self.min_sum:
                raise ValidationError(
                    f"Parameter '{param_name}' sum must be at least {self.min_sum}"
                )
        return wrapper(value)
```

## Error Handling

py-enforce raises specific exceptions for different validation failures:

- `ValidationError`: Raised when validation logic fails
- `TypeError`: Raised when a validator is used on an incompatible type

```python
from py_enforce import ValidationError

try:
    greet("")  # Empty string
except ValidationError as e:
    print(f"Validation failed: {e}")
except TypeError as e:
    print(f"Type error: {e}")
```

## Requirements

- Python 3.13 or higher

## Development

Clone the repository and set up the development environment:

```bash
git clone https://github.com/your-username/py-enforce.git
cd py-enforce
uv sync
```

Run tests:

```bash
uv run pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
