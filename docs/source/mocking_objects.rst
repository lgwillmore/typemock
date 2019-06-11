Mocking an Object
=================

The `DSL` for defining and using **typemock** takes much of its inspiration from the mocking libraries of statically typed languages.
This may change... but it we think it provides a clear way of expressing what it is we are mocking.

First, let us define a class that we wish to mock.

.. code-block:: python

    class MyThing:

        def return_a_str(self) -> str:
            pass

        def convert_int_to_str(self, number: int) -> str:
            pass

        def concat(self, prefix: str, number: int) -> str:
            pass

        def do_something_with_side_effects(self) -> None:
            pass

To mock a class, we use the `tmock` function. This returns a mock instance of the provided class type. This is actually a context manager, and you need to open the context to specify any behaviour.

.. note::
    You must specify the behaviour of any method that your test is going to interact with. Interacting with a method with no specified behaviour results in an error.

Let us mock our class and define some behaviour.

Simple response
---------------

.. code-block:: python

    expected_result = "a string"

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.return_a_str()).then_return(expected_result)

    actual = my_thing_mock.return_a_str()

    assert expected_result = actual

We also let the context of the mock close before we interacted with it, and it returned the response we had defined.

Different responses for different args
--------------------------------------

We can also specify different responses for different sets of method arguments as follows.

.. code-block:: python

    result_1 = "first result"
    result_2 = "second result"

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.convert_int_to_str(1)).then_return(result_1)
        when(my_thing_mock.convert_int_to_str(2)).then_return(result_2)

    assert result_1 = my_thing_mock.convert_int_to_str(1)
    assert result_2 = my_thing_mock.convert_int_to_str(2)


Series of responses
-------------------

We can specify a series of responses for successive calls to a method with the same matching args.

.. code-block:: python

    responses = [
        "first result"
        "second result"
    ]

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.convert_int_to_str(1)).then_return_many(responses)


    for response in responses:
        assert response = my_thing_mock.convert_int_to_str(1)


By default, if we interact with the method more than the specified series, we will get an error. But you can set this to looping with the `loop` parameter for `then_return_many` responder.

Error responses
---------------

We can also make our mock raise an Exception.

.. code-block:: python

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.return_a_str()).then_raise(IOError)

    my_thing_mock.return_a_str()  # <- Error raised here.

Arg Matching
------------

Sometimes we want to be more general in the arguments needed to trigger a response. There is currently only the `match.anything()` matcher.


.. code-block:: python

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.convert_int_to_str(match.anything())).then_return("hello")

    assert "hello" = my_thing_mock.convert_int_to_str(1)
    assert "hello" = my_thing_mock.convert_int_to_str(2)

Despite using this very broad matcher, any interactions with the mock will throw errors if they receive incorrectly typed args in their interactions.
