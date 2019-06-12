Type Safety
===========

The introduction of type hints to python is great. Not that it is a new thing.

Some of the benefits include:

 - Clear documentation of the interface of a module, object, function.
 - Better IDE tooling. You can drill into the code and investigate how things all wire up when things are explicit.
 - Depending on the completeness of your type hints, a reduction in certain types of bugs, and less tests needed to try and avoid them in the first place.

Mypy is an excellent tool for really getting the most out of type hints, and we think it would be great if every project ran the mypy linter on strict mode :D but there might be a bit of bias in that.

Imagine if every client library was fully type hinted, and you have type safe mocking? This is not a replacement for some level of integration testing, but it means you can conduct much higher fidelity tests on a mock of the client without the need for some sort of sandbox or dockerized service.

And so, typemock follows in the mypy philosophy with completely type hinted code as something to aim for. Typemock operates in a `strict` mode by default.

Strict
------

Strict mode means that when you try to mock a given class, and that class is not fully type hinted, you will get an error.

The error will highlight what type hints are missing from your class. Lets look at an example.

//TODO: Look at `strict`, `return_none`, and `relaxed`. (the functionality is there to use if you are having issues, you just need to find it)

No return is None return
------------------------

//TODO:


Relaxed
-------

//TODO:

During mocking
--------------

//TODO:
