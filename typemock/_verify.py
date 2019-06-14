from typing import Callable, Generic, cast

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
    _tmock_initialised = False

    def __init__(self, mock: _MockObject[T], exactly: int):
        self._mock = mock
        self._exactly = exactly
        for method_state in mock._mock_method_states:
            verify_method = _verify_method(method_state, exactly)
            bind(self, verify_method, method_state.name)
        self._tmock_initialised = True

    def __getattribute__(self, item: str):
        if object.__getattribute__(self, "_tmock_initialised"):
            mock = object.__getattribute__(self, "_mock")
            exactly = object.__getattribute__(self, "_exactly")
            if item in mock._mock_attribute_states:
                state = mock._mock_attribute_states[item]
                get_calls = state.call_count_gets()
                if exactly == -1:
                    if get_calls < 1:
                        raise VerifyError(
                            "There were no gets of attribute: {}".format(
                                state.name
                            )
                        )
                    else:
                        return
                else:
                    if get_calls != exactly:
                        if get_calls == 0:
                            message = "There were no gets for attribute: {}".format(
                                state.name
                            )
                        else:
                            message = "There were {} gets for attribute: {}".format(
                                get_calls, state.name
                            )
                        raise VerifyError(message)
                    else:
                        return
        return object.__getattribute__(self, item)

    def __setattr__(self, key, item):
        if self._tmock_initialised:
            mock = self._mock
            exactly = self._exactly
            if key in mock._mock_attribute_states:
                state = mock._mock_attribute_states[key]
                called_set_record = state.called_set_record(item)
                if exactly == -1:
                    if called_set_record.count < 1:
                        raise VerifyError(
                            "There were no set interactions for attribute: {} with arg: {} and there were {} other interactions".format(
                                state.name, called_set_record.call, called_set_record.other_call_count
                            )
                        )
                    else:
                        return
                else:
                    if called_set_record.count != exactly:
                        if called_set_record.count == 0:
                            message = "There were no set interactions for attribute: {} with arg: {} and there were {} other interactions".format(
                                state.name, called_set_record.call, called_set_record.other_call_count
                            )
                        else:
                            message = "There were {} set interactions for attribute: {} with arg: {}".format(
                                called_set_record.count, state.name, called_set_record.call
                            )
                        raise VerifyError(message)
                    else:
                        return
        else:
            object.__setattr__(self, key, item)


def _verify(mock: T, exactly: int = -1) -> T:
    return cast(T, _VerifyObject(cast(_MockObject[T], mock), exactly=exactly))
