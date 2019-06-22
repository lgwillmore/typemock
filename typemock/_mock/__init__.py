from types import FunctionType
from typing import Union, Type, cast, TypeVar, Awaitable

from typemock._mock.object import MockObject
from typemock.api import MockingError, TypeSafety, ResponseBuilder

T = TypeVar('T')
R = TypeVar('R')

_error_when_context_closed = """
Did not receive a response builder.

Are you trying to specify behaviour outside of the mock context?
"""

_error_when_async_not_awaited = """

Did not receive a response builder.

You need to await async functions when defining behaviour of the mock. Example:

    with tmock(MyAsyncThing) as my_async_mock:
        when(await my_async_mock.get_an_async_result()).then_return(expected)

"""


def _tmock(clazz: Union[Type[T], T], type_safety: TypeSafety = TypeSafety.STRICT) -> T:
    """
    Mocks a given class.

    This must be used as a context in order to define the mocked behaviour with `when`.

    You must let the context close in order to use the mocked object as intended.

    Examples:

        with tmock(MyClass) as my_mock:
            when(my_mock.do_something()).then_return("A Result")

        result = my_mock.do_something()

    Args:

        type_safety:
        clazz:

    Returns:

        mock:

    """
    if isinstance(clazz, FunctionType):
        raise MockingError("Cannot mock a {} for now. Only objects and classes supported".format(clazz))
    return cast(T, MockObject(clazz, type_safety))


def _when(mock_call_result: T) -> ResponseBuilder[T]:
    """
    Hook for initializing behaviour mocking builder.

    Args:
        mock_call_result:

    Returns:

    """
    if not isinstance(mock_call_result, ResponseBuilder):
        if isinstance(mock_call_result, Awaitable):
            raise MockingError(_error_when_async_not_awaited)
        raise MockingError(_error_when_context_closed)
    return cast(ResponseBuilder[T], mock_call_result)
