from unittest import TestCase

import trio as trio

from typemock import tmock, when, verify


class MyAsyncThing:

    async def get_an_async_result(self) -> str:
        pass


def async_test(f):
    """
    An annotation for running an async test case with the trio.
    """

    def wrapper(*args):
        result = trio.run(f, *args)
        return result

    return wrapper


class TestAsyncMocking(TestCase):

    @async_test
    async def test_we_can_mock_and_verify_an_async_method(self):
        expected = "Hello"

        with tmock(MyAsyncThing) as my_async_mock:
            when(await my_async_mock.get_an_async_result()).then_return(expected)

        self.assertEqual(expected, await my_async_mock.get_an_async_result())

        verify(my_async_mock).get_an_async_result()
