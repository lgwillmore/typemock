from typing import Callable, Generic, cast, TypeVar

from typemock._mock import MockObject
from typemock._mock.methods import MockMethodState
from typemock._utils import bind
from typemock.api import VerifyError

T = TypeVar('T')

_error_no_interactions_with_others = """

No interactions with method '{method_name}' for arguments:

{expected_args}

{count} other interaction(s):

[
    {first_other}
...
]

"""

_error_no_interactions = """

No interactions with method '{method_name}' for arguments:

{expected_args}

No other interactions.

"""

_error_incorrect_amount_of_interactions_others = """

Expected {expected_count} interactions with '{method_name}' with args:

{expected_args}

But there were {actual_interactions} interactions.

And {other_count} other interaction(s):

[
    {first_other}
...
]

"""

_error_incorrect_amount_of_interactions = """

Expected {expected_count} interactions with '{method_name}' with args:

{expected_args}

But there were {actual_interactions} interactions. No other interactions.

"""

_error_no_sets_others = """

No sets for attribute '{attribute_name}' with {expected_args}.

{count} other interaction(s):

[
    {first_other}
...
]

"""

_error_no_sets = """

No sets for attribute '{attribute_name}' with {expected_args}.

No other `sets`.

"""

_error_incorrect_sets_others = """

Expected {expected_count} `sets` for  '{attribute_name}' with arg: {expected_args}

But there were {actual_interactions} `sets`.

And {other_count} other `sets`(s):

[
    {first_other}
...
]

"""

_error_incorrect_sets = """

Expected {expected_count} `sets` for  '{attribute_name}' with arg: {expected_args}

But there were {actual_interactions} `sets`.

No other `sets`.

"""


def _verify_method(method_state: MockMethodState, exactly: int) -> Callable:
    def method_mock(*args, **kwargs):
        call_count = method_state.call_count_for(*args, **kwargs)
        if exactly == -1:
            if call_count.count < 1:
                if len(call_count.other_calls) > 0:
                    raise VerifyError(
                        _error_no_interactions_with_others.format(
                            method_name=method_state.name,
                            expected_args=call_count.call,
                            count=len(call_count.other_calls),
                            first_other=call_count.other_calls[0]
                        )
                    )
                else:
                    raise VerifyError(
                        _error_no_interactions.format(
                            method_name=method_state.name,
                            expected_args=call_count.call
                        )
                    )
        else:
            if call_count.count != exactly:
                if len(call_count.other_calls) > 0:
                    raise VerifyError(
                        _error_incorrect_amount_of_interactions_others.format(
                            method_name=method_state.name,
                            expected_args=call_count.call,
                            other_count=len(call_count.other_calls),
                            first_other=call_count.other_calls[0],
                            expected_count=exactly,
                            actual_interactions=call_count.count
                        )
                    )
                else:
                    raise VerifyError(
                        _error_incorrect_amount_of_interactions.format(
                            method_name=method_state.name,
                            expected_count=exactly,
                            actual_interactions=call_count.count,
                            expected_args=call_count.call
                        )
                    )

    return method_mock


class _VerifyObject(Generic[T]):
    _tmock_initialised = False

    def __init__(self, mock: MockObject[T], exactly: int):
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
                            "\nThere were no gets of attribute: {}\n".format(
                                state.name
                            )
                        )
                    else:
                        return
                else:
                    if get_calls != exactly:
                        if get_calls == 0:
                            message = "\nThere were no gets for attribute: {}. Expecting {}\n".format(
                                state.name, exactly
                            )
                        else:
                            message = "\nThere were {} gets for attribute: {}. Expecting {}\n".format(
                                get_calls, state.name, exactly
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
                        if len(called_set_record.other_calls) > 0:
                            raise VerifyError(
                                _error_no_sets_others.format(
                                    attribute_name=state.name,
                                    expected_args=called_set_record.call,
                                    count=len(called_set_record.other_calls),
                                    first_other=called_set_record.other_calls[0]
                                )
                            )
                        else:
                            raise VerifyError(
                                _error_no_sets.format(
                                    attribute_name=state.name,
                                    expected_args=called_set_record.call
                                )
                            )

                    else:
                        return
                else:
                    if called_set_record.count != exactly:
                        if len(called_set_record.other_calls) > 0:
                            raise VerifyError(
                                _error_incorrect_sets_others.format(
                                    attribute_name=state.name,
                                    expected_args=called_set_record.call,
                                    expected_count=exactly,
                                    other_count=len(called_set_record.other_calls),
                                    first_other=called_set_record.other_calls[0],
                                    actual_interactions=called_set_record.count
                                )
                            )
                        else:
                            raise VerifyError(
                                _error_no_sets.format(
                                    attribute_name=state.name,
                                    expected_args=called_set_record.call
                                )
                            )
                    else:
                        return
        else:
            object.__setattr__(self, key, item)


def _verify(mock: T, exactly: int = -1) -> T:
    return cast(T, _VerifyObject(cast(MockObject[T], mock), exactly=exactly))
