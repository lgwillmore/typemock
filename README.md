# type-mock

Type safe mocking for python 3.

1. [Motivation](#motivation)
2. [Quick example usage](#quick-example-usage)
3. [Still to do](#still-to-do)

**NOTE: This library is still at the experimental stage. Its API and implementation could change drastically between versions. In fact, it does not quite do what it claims to do yet.**


## Motivation

The mocking tools in python are powerful and useful for building independent tests at various levels.

However, it is possible to build mocks which do not conform to the actual behaviour or contract defined by the things they are mocking. Or, for them to be initially correct, and then to go out of sync with actual behaviour and for tests to remain green.

This is not a symptom of the mocking tools being "bad" per say, it is a symptom of dynamically typed languages. We do not have compile time protections for us doing things with things which do not align with the contracts they define.

But, in python, we now have type hints. And so, we can explicitly define the contracts of our objects, and, if we have done this, we can mock them in a type safe way as well. This is what this library aims to help achieve. Type safe mocking.


## Quick Example Usage

Given a class such some class (the implementation of its method is not relevant)

```python
class MyThing:
    
    def multiple_arg(self, prefix: str, number: int) -> str:
        pass
```
            
            
We con mock behaviour and verify interactions:

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

## Still to do

 - Enforce type hinted mocked objects by default, with option to disable
 - Check types at point of behaviour definition, and during mocked usage.
 - More advanced argument matching
 - More verification options



