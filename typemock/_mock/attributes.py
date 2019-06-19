from typing import Any, Generic, Type, List, TypeVar, Tuple

from typemock._mock.responders import Responder, ResponderBasic, ResponderMany, ResponderRaise, ResponderDo
from typemock._utils import Blank, is_type
from typemock.api import MockTypeSafetyError, DoFunction
from typemock.api import ResponseBuilder

T = TypeVar('T')
R = TypeVar('R')


class CalledSetRecord:

    def __init__(self, call: Any, count: int, other_call_count: int):
        self.call = call
        self.count = count
        self.other_call_count = other_call_count


def _null_ordered_call(*args, **kwargs) -> Tuple[Tuple[str, Any], ...]:
    return tuple([])


class MockAttributeState(Generic[R]):

    def __init__(self, name: str, initial_value: R, type_hint: Type):
        self.name = name
        self.type_hint = type_hint
        self._responder: Responder = ResponderBasic(initial_value)
        self._call_count = 0
        self._set_calls: List[R] = []

    def _validate_return(self, response: R):
        if not isinstance(self.type_hint, Blank):
            if not is_type(response, self.type_hint):
                raise MockTypeSafetyError("Attribute: {} must be of type:{}".format(
                    self.name,
                    self.type_hint,
                ))

    def set_response(self, response: R):
        self._validate_return(response)
        self._responder = ResponderBasic(response)

    def set_response_many(self, results: List[R], loop: bool):
        for response in results:
            self._validate_return(response)
        self._responder = ResponderMany(results, loop)

    def set_error_response(self, error: Exception):
        self._responder = ResponderRaise(error)

    def set_response_do(self, do_function: DoFunction):
        self._responder = ResponderDo(do_function, _null_ordered_call)

    def response(self) -> R:
        self._call_count += 1
        r = self._responder.response()
        self._validate_return(r)
        return r

    def call_count_gets(self) -> int:
        return self._call_count

    def called_set_with(self, item):
        self._validate_return(item)
        self._set_calls.append(item)
        self._responder = ResponderBasic(item)

    def called_set_record(self, expected_call) -> CalledSetRecord:
        other_count = 0
        count = 0
        for call in self._set_calls:
            if expected_call == call:
                count += 1
            else:
                other_count += 1
        return CalledSetRecord(expected_call, count, other_count)


class AttributeResponseBuilder(Generic[R], ResponseBuilder[R]):

    def __init__(self, attribute_state: MockAttributeState):
        self._attribute_state = attribute_state

    def then_return(self, result: R) -> None:
        self._attribute_state.set_response(result)

    def then_raise(self, error: Exception) -> None:
        self._attribute_state.set_error_response(error)

    def then_return_many(self, results: List[R], loop: bool = False) -> None:
        self._attribute_state.set_response_many(results, loop)

    def then_do(self, do_function: DoFunction) -> None:
        self._attribute_state.set_response_do(do_function)
