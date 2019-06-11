A quick intro
=============

Given some class (the implementation of its method is not relevant)

.. code-block:: python

    class MyThing:

        def multiple_arg(self, prefix: str, number: int) -> str:
            pass

Mock and Verify
---------------
We con mock behaviour and verify interactions as follows:

.. code-block:: python

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

Things to note:

 - The mocked object must be used as a context manager in order to specify behaviour.
 - You must let the context close in order to use the defined behaviour.

Type safety
-----------
And when we try to specify behaviour that does not conform to the contract of the object we are mocking

.. code-block:: python

    expected_result = "a string"

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.multiple_arg(prefix="p", number="should be an int")).then_return(expected_result)


We get an informative error such as::

    typemock.safety.MockTypeSafetyError: Method: multiple_arg Arg: number must be of type:<class 'int'>

Things to note:

 - You will also get type hint errors if you attempt to specify behaviour that returns the incorrect type.

