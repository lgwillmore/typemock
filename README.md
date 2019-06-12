# typemock

[![Build Status](https://travis-ci.com/lgwillmore/typemock.svg?branch=master)](https://travis-ci.com/lgwillmore/typemock) [![Documentation Status](https://readthedocs.org/projects/typemock/badge/?version=latest)](https://typemock.readthedocs.io/en/latest/?badge=latest)

Type safe mocking for python 3.

1. [Motivation](#motivation)
2. [Quick example usage](#quick-example-usage)
3. [Still to do](#still-to-do)

**NOTE: This library is still in Alpha. Its API and implementation could change.**

[Detailed Documentation](typemock.readthedocs.io)

## Motivation

The mocking tools in python are powerful and useful for building independent tests at various levels.

However, it is possible to build mocks which do not conform to the actual behaviour or contract defined by the things they are mocking. Or, for them to be initially correct, and then to go out of sync with actual behaviour and for tests to remain green.

This is not a symptom of the mocking tools being "bad" per say, it is a symptom of dynamically typed languages. We do not have compile time protections for us doing things with things which do not align with the contracts they define.

But, in python, we now have type hints. And so, we can explicitly define the contracts of our objects, and, if we have done this, we can mock them in a type safe way as well. This is what this library aims to help achieve. Type safe mocking.


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

Things to note:

 - The mocked object must be used as a context manager in order to specify behaviour.
 - You must let the context close in order to use the defined behaviour.
 
### Type safety

And when we try to specify behaviour that does not conform to the contract of the object we are mocking

```python
expected_result = "a string"

with tmock(MyThing) as my_thing_mock:
    when(my_thing_mock.multiple_arg(prefix="p", number="should be an int")).then_return(expected_result)
```

We get an informative error such as

    typemock.safety.MockTypeSafetyError: Method: multiple_arg Arg: number must be of type:<class 'int'>

Things to note:

 - You can only mock objects which have fully type hinted interfaces. You will get Type hint errors otherwise.
 - You will also get type hint errors if you attempt to specify behaviour that returns the incorrect type.


## Still to do

 - Mock attributes and properties.
 - Check/implement more complex type safety (nested objects)
 - More behaviour specifications (Programmatic responses)
 - Better docs and examples



