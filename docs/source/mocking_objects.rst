Mocking an Object
=================

The `DSL` for defining and using **typemock** takes much of its inspiration from the mocking libraries of statically typed languages, kotlin's mockk library in particular.

To mock a class or object, we use the `tmock` function. This returns a mock instance of the provided class type. This is actually a context manager, and you need to open the context to specify any behaviour.

You can pass a class or an instance of the class to the `tmock` function to be mocked. So...

.. code-block:: python

    with tmock(MyThing) as my_mock:

        # define mock behaviour

and:

.. code-block:: python

    with tmock(MyThing()) as my_mock:

        # define mock behaviour

are both acceptable.

There will be cases where, if an instance of the class has complex `__init__` functionality, then mocking a class will not be able to discover instance level attributes. In this case, you can attempt to mock an already initialised instance to resolve this. See more in the `Mocking Attributes`_ section.

.. note::

    - You must specify the behaviour of any method that your test is going to interact with. Interacting with a method with no specified behaviour results in an error.
    - Typemock does not do static patching of the class being mocked. Any mocked behaviour will only be available fro the mock instance itself, not via a class accessed call.
    - Instance level attributes might not be available if the `__init__` method has some more complex logic. Use an already instantiated object in this case.

Now lets look at how to specify the behaviour for a mocked class or object.

Mocking Methods
###############

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

Simple response
---------------

.. code-block:: python

    expected_result = "a string"

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.return_a_str()).then_return(expected_result)

    actual = my_thing_mock.return_a_str()

    assert expected_result == actual

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

    assert result_1 == my_thing_mock.convert_int_to_str(1)
    assert result_2 == my_thing_mock.convert_int_to_str(2)


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
        assert response == my_thing_mock.convert_int_to_str(1)


By default, if we interact with the method more than the specified series, we will get an error. But you can set this to looping with the `loop` parameter for `then_return_many` responder.

Programmatic response
---------------------

You can provide dynamic responses through a function handler.

The function should have the same signature as the method it is mocking so that mixes of positional and keyword arguments are handled in a deterministic way.

.. code-block:: python

    def bounce_back_handler(number: int) -> str:
        return "{}".format(number)

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.convert_int_to_str(1)).then_do(bounce_back_handler)

    assert "1" == my_thing_mock.convert_int_to_str(1)

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

    assert "hello" == my_thing_mock.convert_int_to_str(1)
    assert "hello" == my_thing_mock.convert_int_to_str(2)

Despite using this very broad matcher, any interactions with the mock will throw errors if they receive incorrectly typed args in their interactions.

Mocking async methods
---------------------

We can also mock async methods. It just requires the addition an `await` key word when defining the behaviour. Here is an example:

.. code-block:: python

    #  Given some object with async methods.

    class MyAsyncThing:

        async def get_an_async_result(self) -> str:
            pass

    # We can setup and verify in an async test case.

    async def my_test(self):
        expected = "Hello"

        with tmock(MyAsyncThing) as my_async_mock:
            when(await my_async_mock.get_an_async_result()).then_return(expected)

        assert expected == await my_async_mock.get_an_async_result())

        verify(my_async_mock).get_an_async_result()


.. note::
    The the verify call does not need the `await` key word.

Mocking Attributes
##################

Attributes are a little trickier than methods, given the layered namespaces of an instance of a class and the class itself.

With methods we can find the public members and their signatures regardless of if we are looking at an instance or a class.
The state of a given instance/class implementation ie. its attributes can be defined in several ways, and so their type hints can be defined or deduced in several ways.

For now, `typemock` does its best to determine the type hints of attributes, and where it cannot, it is treated as untyped. Let's look at an example class to see what type hints are discoverable.

.. code-block:: python

    class MyThing:
        class_att = "foo"  # <- not typed
        class_att_with_type: int = 1  # <- typed, easy
        class_att_with_typed_init = "bar"  # <- type determined from __init__ annotation.
        class_att_with_untyped_init = "wam"  # <- not typed

        def __init__(
                self,
                class_att_with_typed_init: str,  # <- provides type for class level attribute
                class_att_with_untyped_init,  # <- no type for class level attribute
                instance_att_typed_init: int,  # <- provides type for instance attribute
                instance_att_untyped_init,  # <- not typed
        ):
            self.class_att_with_typed_init = class_att_with_typed_init
            self.class_att_with_untyped_init = class_att_with_untyped_init  # <- not typed
            self.instance_att_typed_init = instance_att_typed_init  # <- type from init
            self.instance_att_untyped_init = instance_att_untyped_init  # <- not typed
            self.instance_att_no_init: str = "hello"  # <- has a type hint, but not discoverable = not typed

It might take some time to digest that, but essentially, effective attribute type hinting takes place either at a class level, or in the `__init__` method signature.

If you pass in a class to the `tmock` function, typemock will try to instantiate an instance of the class so that it can discover instance level attributes. If some more complicated logic occurs in the `__init__` method though, typemock may not be able to do this, and will log a warning.
In this case, if you want to mock an instance level attribute you will need to provide an already instantiated instance to the `tmock` function.


To some up the basic guidelines for mocking attributes:

    - Define your type hints at a class level or in the `__init__` method signature.
    - If the `__init__` method of the class has some more complex logic, you may need to provide an instantiated instance to `tmock`

Depending on how this works in practice this may change, or some config may be introduced to assume attribute types from initial values.

With that quirkiness explained to some extent, let us look at how to actually mock an attribute. We will use this simpler class for the examples:

.. code-block:: python

    class MyThing:

            name: str = "anonymous"


.. note::

    Currently, it is also not necessary to always specify behaviour of an attribute. It will by default return the value it was initialised with.

Simple Get
----------

Just as with a method call, we can specify the response of a `get`.

.. code-block:: python

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.name).then_return("foo")

    assert my_thing_mock.name == "foo"


Get Many
--------

.. code-block:: python

    expected_results = [
       "foo",
       "bar"
    ]

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.name).then_return_many(expected_results)

    for expected in expected_results:
        assert my_thing_mock.name == expected

You can also provide the `loop=True` arg to make this behaviour loop through the list.


Get Raise
----------

.. code-block:: python

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.name).then_raise(IOError)

    my_thing_mock.name  # <- Error raised here.

Get programmatic response
-------------------------

As with methods, you can provide dynamic responses through a function handler.

It might be useful if you do want to wire up some stateful mocking/faking or have some other dependency.

.. code-block:: python

    def name_get_handler():
        return "my name"

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.name).then_do(name_get_handler)

    assert "my name" == my_thing_mock.name

