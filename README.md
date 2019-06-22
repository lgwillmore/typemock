# typemock

[![Build Status](https://travis-ci.com/lgwillmore/typemock.svg?branch=master)](https://travis-ci.com/lgwillmore/typemock) [![Documentation Status](https://readthedocs.org/projects/typemock/badge/?version=latest)](https://typemock.readthedocs.io/en/latest/?badge=latest) [![Pyversions](https://img.shields.io/pypi/pyversions/typemock.svg?style=flat-square)](https://pypi.python.org/pypi/typemock)

Type safe mocking for python 3.

1. [Motivation](#motivation)
2. [Installation](#installation)
3. [Quick example usage](#quick-example-usage)

**NOTE: This library is still in Alpha. Its API and implementation could change.**

[Detailed Documentation](https://typemock.readthedocs.io)

## Motivation

The mocking tools in python are powerful, flexible and useful for building independent tests at various levels.

This flexibility is part of what is considered a strength of the python language, and possibly any dynamically typed language.

However, this flexibility comes at a cost.

It is possible to build mocks which do not conform to the actual behaviour or contract defined by the things they are mocking. Or, for them to be initially correct, and then to go out of sync with actual behaviour and for tests to remain green.

We do not have compile time protections for us doing things with/to things which do not align with the contracts they define and the clients of those contracts expect.

But, now we have type hints. And so, we can explicitly define the contracts of our objects, and, if we have done this, we can mock them in a type safe way as well. This is what this library aims to help achieve. Type safe mocking.

Used in conjunction with mypy, this should result in much more high fidelity independent tests.

## Installation

    pip install typemock

## Quick Example Usage

Given some class (the implementation of its method is not relevant)

```python
class MyThing:
    
    def multiple_arg(self, prefix: str, number: int) -> str:
        pass
```

### Mock and verify

We con mock behaviour and verify interactions as follows:

```python
from typemock import tmock, when, verify

expected_result = "a string"

with tmock(MyThing) as my_thing_mock:
    when(my_thing_mock.multiple_arg("p", 1)).then_return(expected_result)

actual = my_thing_mock.multiple_arg(
    number=1,
    prefix="p"
)

assert expected_result == actual
verify(my_thing_mock).multiple_arg("p", 1)

```

### Type safety

And when we try to specify behaviour that does not conform to the contract of the object we are mocking

```python
expected_result = "a string"

with tmock(MyThing) as my_thing_mock:
    when(my_thing_mock.multiple_arg(prefix="p", number="should be an int")).then_return(expected_result)
```

We get an informative error such as

    typemock.safety.MockTypeSafetyError: Method: multiple_arg Arg: number must be of type:<class 'int'>





