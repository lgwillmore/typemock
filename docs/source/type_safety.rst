Type Safety
===========

The introduction of type hints to python is great.

Some of the benefits include:

 - Clear documentation of the interface of a module, object, function.
 - Better IDE tooling. You can drill into the code and investigate how things all wire up when things are explicit.
 - Depending on the completeness of your type hints, a reduction in certain types of bugs, and less tests needed to try and avoid them in the first place.

Mypy is an excellent tool for really getting the most out of type hints, and we think it would be great if every project ran the mypy linter on strict mode :D - at least for the public parts of their api.

With a full type hinting, and type safe mocking, the fidelity of your independent internal unit tests can drastically improve.

Also, consider a fully type hinted client to some 3rd party service. A service that does not provide some sort of sandbox or dockerised instance to test against? With type safe mocking of that client, you can now achieve high fidelity tests in this case as well.

We are not suggesting this as a replacement for some sort of integration test if it is possible, but it offers big improvements for a quick lightweight test that can be run independently.

.. note::

    It is also worth mentioning, that running the mypy linter over your type hinted code is also definitely recommended. Regardless of using typemock for your tests.
    This is key to making sure that your implementations conform to the interface/contract they claim to implement.

Because typemock is aiming to improve type safety it operates in a `strict` mode by default. This section will describe what that means, what other modes are available and how they work in practice.

Strict
------

.. code-block:: python

    TypeSafety.STRICT

Strict mode means that when you try to mock a given class, and that class is not fully type hinted, you will get an error. This is the default.

The error will highlight what type hints are missing from the class you are trying to mock. If the class is in your codebase, you can then add them, or if you do not have control over that class, you can look at the other modes for easing up on the type safety.

Lets look at an example.

.. code-block:: python

    class ClassWithMultipleUnHintedThings:

        def _some_private_function(self):
            # We do not care about type hints for private methods
            pass

        def good_method_with_args_and_return(self, number: int) -> str:
            pass

        def good_method_with_no_args_and_return(self) -> str:
            pass

        def method_with_missing_arg_hint(self, something, something_else: bool) -> None:
            pass

        def method_with_missing_return_type(self):
            pass


    with tmock(ClassWithMultipleUnHintedThings) as my_mock: # <- MissingTypeHintsError here.
        # Set up mocked behaviour here
        pass

With this class, there are multiple missing type hints. And when we try to mock it with the default strict mode, we will get error output as follows::

    typemock.api.MissingTypeHintsError: ("<class 'test_safety.ClassWithMultipleUnHintedThings'> has missing type hints.", [MissingHint(path=['method_with_missing_arg_hint', 'something'], member_type=arg), MissingHint(path=['method_with_missing_return_type'], member_type=return)])

We can see that we are missing argument and return type hints. We should try to add those type hints if we can, but if we cannot, we can look at the other type safety modes.


No return is None return
------------------------

.. code-block:: python

    TypeSafety.NO_RETURN_IS_NONE_RETURN


This mode lets us be lenient towards methods which do not define a return type. It does however assume that an undefined return type is a return type of `None`.

Here is an example.

.. code-block:: python

    class NoReturnTypes:

        def method_with_missing_return_type(self):
            pass


    with tmock(NoReturnTypes, type_safety=TypeSafety.NO_RETURN_IS_NONE_RETURN) as my_mock:
        when(my_mock.method_with_missing_return_type()).then_return(None)


This will no longer raise a `MissingTypeHintsError`. If there were missing argument hints though, it would.

Relaxed
-------

.. code-block:: python

    TypeSafety.RELAXED


This is the most permissive of the type safety modes. It will allow for a completely unhinted class to be mocked. Obviously many of the benefits of type hinting and type safe mocking are lost in this case.

During mocking
--------------

Typemock also offers type safety at the point at which you specify the behaviour of your mock. And this is probably the most crucial part of it.

If the class you are mocking is type hinted, you cannot make it accept arguments which do not conform to the types expected, and you cannot make the methods return something that is of the incorrect type.

Some examples, given the following class to mock.

.. code-block:: python

    class MyThing:

        def convert_int_to_str(self, number: int) -> str:
            pass



And we try to specify an incorrect argument type to match against.

.. code-block:: python

    with tmock(MyThing) as my_mock:
        when(my_mock.convert_int_to_str("not an int")).then_return("hello")

We will get the following error::

    typemock.api.MockTypeSafetyError: Method: convert_int_to_str Arg: number must be of type:<class 'int'>

And if we try to specify the incorrect return type.

.. code-block:: python

    not_a_string = 3

    with tmock(MyThing) as my_mock:
        when(my_mock.convert_int_to_str(1)).then_return(not_a_string)

We will get this error::

    typemock.api.MockTypeSafetyError: Method: convert_int_to_str return must be of type:<class 'str'>

And so, in summary, with typemock on strict mode and good type hints, it becomes difficult to make a mock that does something it should not do.
