from typing import Callable, Generic

from typemock._mock import _MockMethodState, T, _MockObject
from typemock._utils import bind
from typemock.api import VerifyError


def _verify_method(method_state: _MockMethodState, exactly: int = -1) -> Callable:
    def method_mock(*args, **kwargs):
        call_count = method_state.call_count_for(*args, **kwargs)
        if exactly == -1:
            if call_count < 1:
                raise VerifyError()
        else:
            if call_count != call_count:
                raise VerifyError()

    return method_mock


class _VerifyObject(Generic[T]):

    def __init__(self, mock: _MockObject[T]):
        for method_state in mock._mock_method_states:
            verify_method = _verify_method(method_state)
            bind(self, verify_method, method_state.name)


def verify(mock: T) -> T:
    return _VerifyObject(mock)
