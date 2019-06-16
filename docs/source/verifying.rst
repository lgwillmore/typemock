Verifying
=========

Verification is important for checking that an interaction did or did not happen, or if it happened a specific amount of times. It can also allow for checking that interactions happened in a particular order.

Typemock currently only has quite limited verification, but it is good for most use cases.


Verifying Methods
#################

Given the following class to mock:

.. code-block:: python

    class MyThing:

        def convert_int_to_str(self, number: int) -> str:
            pass


We can verify method interactions in the following ways:

At least once
-------------

We can assert that an interaction happened at least once.

.. code-block:: python

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.convert_int_to_str(match.anything())).then_return("something")

    # Logic under test is called.

    verify(my_thing_mock).convert_int_to_str(3)



Exactly
-------

We can assert that an interaction happened a specific number of times.

.. code-block:: python

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.convert_int_to_str(match.anything())).then_return("something")

    # Logic under test is called.

    verify(my_thing_mock, exactly=2).convert_int_to_str(3)


Never called
------------

We can assert that an interaction never happened by checking for 0 calls.

.. code-block:: python

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.convert_int_to_str(match.anything())).then_return("something")

    # Logic under test is called.

    verify(my_thing_mock, exactly=0).convert_int_to_str(3)


Any calls
---------

And all of the previous examples have been verifying calls with specific args. We can also use the `match.anything` matcher to check for any interactions.

.. code-block:: python

    with tmock(MyThing) as my_thing_mock:
        when(my_thing_mock.convert_int_to_str(match.anything())).then_return("something")

    # Logic under test is called.

    verify(my_thing_mock).convert_int_to_str(match.anything())


Verifying Attributes
####################

Given the following class to mock:

.. code-block:: python

    class MyThing:

            name: str = "anonymous"


We can verify interactions with its attribute as follows.

Get called at least once
------------------------


.. code-block:: python

    my_thing_mock =  tmock(MyThing)

    # Logic under test is called.

    verify(my_thing_mock).name


Get called exact amount of times
--------------------------------


.. code-block:: python

    my_thing_mock =  tmock(MyThing)

    # Logic under test is called.

    verify(my_thing_mock, exactly=2).name

Set called with specific arg
----------------------------

.. code-block:: python

    my_thing_mock =  tmock(MyThing)

    # Logic under test is called.

    verify(my_thing_mock).name = 2


Set called with any arg
-----------------------

.. code-block:: python

    my_thing_mock =  tmock(MyThing)

    # Logic under test is called.

    verify(my_thing_mock).name = match.anything()


Set called exact amount of times
--------------------------------

.. code-block:: python

    my_thing_mock =  tmock(MyThing)

    # Logic under test is called.

    verify(my_thing_mock, exactly=1).name = 2
