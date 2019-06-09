from typing import Callable, Generic

from typemock.mock import MockMethodState, T, MockObject
from typemock.utils import bind


def _verify_method(method_state: MockMethodState, exactly: int = -1) -> Callable:
    def method_mock(*args, **kwargs):
        call_count = method_state.call_count_for(*args, **kwargs)
        if exactly == -1:
            if call_count < 1:
                raise VerifyError()
        else:
            if call_count != call_count:
                raise VerifyError()

    return method_mock


class VerifyObject(Generic[T]):

    def __init__(self, mock: MockObject[T]):
        for method_state in mock._mock_method_states:
            verify_method = _verify_method(method_state)
            bind(self, verify_method, method_state.name)


def verify(mock: T) -> T:
    return VerifyObject(mock)


class VerifyError(Exception):
    pass
