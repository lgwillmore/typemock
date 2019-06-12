from typing import Callable, Generic

from typemock._mock import _MockMethodState, T, _MockObject
from typemock._utils import bind
from typemock.api import VerifyError


def _verify_method(method_state: _MockMethodState, exactly: int) -> Callable:
    def method_mock(*args, **kwargs):
        call_count = method_state.call_count_for(*args, **kwargs)
        if exactly == -1:
            if call_count.count < 1:
                raise VerifyError(
                    "There were no interactions for method: {} with args: {} and there were {} other interactions".format(
                        method_state.name, call_count.call, call_count.other_call_count
                    )
                )
        else:
            if call_count.count != exactly:
                if call_count.count == 0:
                    message = "There were no interactions for method: {} with args: {} and there were {} other interactions".format(
                        method_state.name, call_count.call, call_count.other_call_count
                    )
                else:
                    message = "There were {} interactions for method: {} with args: {}".format(
                        call_count.count, method_state.name, call_count.call
                    )
                raise VerifyError(message)

    return method_mock


class _VerifyObject(Generic[T]):

    def __init__(self, mock: _MockObject[T], exactly: int):
        for method_state in mock._mock_method_states:
            verify_method = _verify_method(method_state, exactly)
            bind(self, verify_method, method_state.name)


def _verify(mock: T, exactly: int = -1) -> T:
    return _VerifyObject(mock, exactly=exactly)
