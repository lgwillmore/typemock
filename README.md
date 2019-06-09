# type-mock

Type safe mocking for python 3.

The mocking tools in python are powerful and useful for building independent tests at various levels.

However, it is possible to build mocks which do not conform to the actual behaviour or contract defined by the things they are mocking. Or, for them to be initially correct, and then to go out of sync with actual behaviour and for tests to remain green.

This is not a symptom of the mocking tools being "bad" per say, it is a symptom of dynamically typed languages. We do not have compile time protections for us doing things with things which do not align with the contracts they define.

But, in python, we do now have type hints. And so, we can explicitly define the contracts of our objects, and, if we have done this, we can mock them in a type safe way as well. This is what this library aims to help achieve. Type safe mocking.


