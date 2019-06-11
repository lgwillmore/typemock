.. typemock documentation master file, created by
   sphinx-quickstart on Tue Jun 11 20:45:13 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

typemock: type safe mocking
===========================

**NOTE: This library is still at the experimental stage. Its API and implementation could change drastically between versions. Currently, only simple object method mocking is possible**

The mocking tools in python are powerful and useful for building independent tests at various levels.

However, it is possible to build mocks which do not conform to the actual behaviour or contract defined by the things they are mocking. Or, for them to be initially correct, and then to go out of sync with actual behaviour and for tests to remain green.

This is not a symptom of the mocking tools being "bad" per say, it is a symptom of dynamically typed languages. We do not have compile time protections for us doing things with things which do not align with the contracts they define.

But, in python, we now have type hints. And so, we can explicitly define the contracts of our objects, and, if we have done this, we can mock them in a type safe way as well. This is what this library aims to help achieve. Type safe mocking.


.. toctree::
   :maxdepth: 2
   :caption: Contents

   quick_intro






