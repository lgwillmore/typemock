.. typemock documentation master file, created by
   sphinx-quickstart on Tue Jun 11 20:45:13 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

typemock: type safe mocking
===========================

.. warning::

   This library is still in Alpha. API and implementation could change.

The mocking tools in python are powerful and useful for building independent tests at various levels.

However, it is possible to build mocks which do not conform to the actual behaviour or contract defined by the things they are mocking. Or, for them to be initially correct, and then to go out of sync with actual behaviour and for tests to remain green.

This is not a symptom of the mocking tools being "bad" per say, it is a symptom of dynamically typed languages. We do not have compile time protections for us doing things with things which do not align with the contracts they define.

But, in python, we now have type hints. And so, we can explicitly define the contracts of our objects, and, if we have done this, we can mock them in a type safe way as well. This is what this library aims to help achieve. Type safe mocking.


.. note:: A small note on the word `mock`

   Yes, in many cases through out the testing world and across languages, the word mock is used incorrectly. We should probably be calling things `Test Doubles`, and if we are only checking interactions occur, then we can call that particular Test Double a mock.

   This is fine, but it probably means that the vast majority of all test doubles are in fact `Fakes` as the only thing you would really be able to mock would be functions with no returns and only side effects. Any test double that returns something is performing some behaviour, and so should probably be classed as a Fake.

   We are going to just ignore all of that. If you want, you can alias the `tmock` function to `ttestdouble` or something like that?

.. toctree::
   :maxdepth: 2

   quick_intro
   mocking_objects
   verifying





