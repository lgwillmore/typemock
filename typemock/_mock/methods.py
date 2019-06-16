import inspect
from inspect import Signature
from types import FunctionType
from typing import Tuple, Any, Generic, Dict, List, Callable, TypeVar

from typemock._mock.responders import Responder, ResponderBasic, ResponderMany, ResponderRaise
from typemock.api import MockTypeSafetyError, NoBehaviourSpecifiedError
from typemock.api import TypeSafety, ResponseBuilder
from typemock.match import Matcher

T = TypeVar('T')
R = TypeVar('R')

OrderedCallValues = Tuple[Tuple[str, Any], ...]


class CallCount:

    def __init__(self, call: OrderedCallValues, count: int, other_call_count: int):
        self.call = call
        self.count = count
        self.other_call_count = other_call_count


def has_matchers(call: OrderedCallValues) -> bool:
    for call_param in call:
        if isinstance(call_param[1], Matcher):
            return True
    return False


class MockMethodState(Generic[R]):

    def __init__(
            self,
            name: str,
            signature: Signature,
            func: FunctionType,
            type_safety: TypeSafety
    ):
        self.name = name
        self.func = func
        self._signature = signature
        self._type_safety = type_safety
        self._responses: Dict[OrderedCallValues, Responder] = {}
        self._matcher_responses: Dict[OrderedCallValues, Responder] = {}
        self._open = False
        self._arg_index_to_arg_name: Dict[int, str] = {}
        self._arg_name_to_parameter: Dict[str, inspect.Parameter] = {}
        self._call_record: List[OrderedCallValues] = []
        i = 0
        for name, param in signature.parameters.items():
            self._arg_index_to_arg_name[i] = name
            self._arg_name_to_parameter[name] = param
            i += 1

    def _ordered_call(self, *args, **kwargs) -> OrderedCallValues:
        if len(args) > len(self._arg_index_to_arg_name):
            raise MockTypeSafetyError("Method: {} cannot be called with args:{} kwargs{}".format(
                self.name,
                args[1:],
                kwargs
            ))
        args_dict = {}
        for i in range(1, len(args)):
            arg = args[i]
            args_dict[self._arg_index_to_arg_name[i]] = arg
        for key, value in kwargs.items():
            if key not in self._arg_name_to_parameter:
                raise MockTypeSafetyError("Method: {} cannot be called with args:{} kwargs{}".format(
                    self.name,
                    args[1:],
                    kwargs
                ))
            args_dict[key] = value
        ordered_key_values = []
        for name, param in self._signature.parameters.items():
            if name == "self":
                continue
            value = args_dict.get(
                name,
                self._arg_name_to_parameter[name].default
            )
            ordered_key_values.append((name, value))
        ordered_call = tuple(ordered_key_values)
        return ordered_call

    def response_for(self, *args, **kwargs) -> R:
        key = self._ordered_call(*args, **kwargs)
        self._call_record.append(key)
        if key in self._responses:
            return self._responses[key].response(*args, **kwargs)
        else:
            for matcher_key, responder in self._matcher_responses.items():
                if matcher_key == key:
                    self._check_key_type_safety(key)
                    return responder.response(*args, **kwargs)
            raise NoBehaviourSpecifiedError(
                "No behaviour specified for method: {} with args: {}".format(self.name, key)
            )

    def call_count_for(self, *args, **kwargs) -> CallCount:
        other_count = 0
        count = 0
        expected_call = self._ordered_call(*args, **kwargs)
        for call in self._call_record:
            if call == expected_call:
                count += 1
            else:
                other_count += 1
        return CallCount(expected_call, count, other_count)

    def _validate_return(self, response: R):
        func_annotations = self.func.__annotations__
        if self._type_safety == TypeSafety.NO_RETURN_IS_NONE_RETURN:
            return_type = func_annotations.get("return")
            if return_type is None:
                if response is not None:
                    raise MockTypeSafetyError("Method: {} return must be of type:{}".format(
                        self.name,
                        return_type,
                    ))
            elif not isinstance(response, return_type):
                raise MockTypeSafetyError("Method: {} return must be of type:{}".format(
                    self.name,
                    return_type,
                ))
        else:
            if "return" in func_annotations:
                return_type = func_annotations["return"]
                if return_type is None:
                    if response is not None:
                        raise MockTypeSafetyError("Method: {} return must be of type:{}".format(
                            self.name,
                            return_type,
                        ))
                elif not isinstance(response, return_type):
                    raise MockTypeSafetyError("Method: {} return must be of type:{}".format(
                        self.name,
                        return_type,
                    ))

    def set_response(self, response: R, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        self._check_key_type_safety(key)
        self._validate_return(response)
        if has_matchers(key):
            self._matcher_responses[key] = ResponderBasic(response)
        else:
            self._responses[key] = ResponderBasic(response)

    def set_response_many(self, results: List[R], loop: bool, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        self._check_key_type_safety(key)
        for response in results:
            self._validate_return(response)
        if has_matchers(key):
            self._matcher_responses[key] = ResponderMany(results, loop)
        else:
            self._responses[key] = ResponderMany(results, loop)

    def set_error_response(self, error: Exception, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        self._check_key_type_safety(key)
        if has_matchers(key):
            self._matcher_responses[key] = ResponderRaise(error)
        else:
            self._responses[key] = ResponderRaise(error)

    def open_for_setup(self):
        self._open = True

    def close_setup(self):
        self._open = False

    def is_open(self) -> bool:
        return self._open

    def _check_key_type_safety(self, key: OrderedCallValues):
        func_annotations = self.func.__annotations__
        for call_arg in key:
            arg_name = call_arg[0]
            arg_value = call_arg[1]
            if isinstance(arg_value, Matcher):
                continue
            if arg_name in func_annotations:
                arg_type = func_annotations[arg_name]
                if not isinstance(arg_value, arg_type):
                    raise MockTypeSafetyError("Method: {} Arg: {} must be of type:{}".format(
                        self.name,
                        arg_name,
                        arg_type
                    ))


def mock_method(state: MockMethodState) -> Callable:
    if inspect.iscoroutinefunction(state.func):
        async def method_mock(*args, **kwargs):
            if state.is_open():
                return MethodResponseBuilder(state, *args, **kwargs)
            else:
                return state.response_for(*args, **kwargs)

        return method_mock
    else:
        def method_mock(*args, **kwargs):
            if state.is_open():
                return MethodResponseBuilder(state, *args, **kwargs)
            else:
                return state.response_for(*args, **kwargs)

        return method_mock


class MethodResponseBuilder(Generic[R], ResponseBuilder[R]):

    def __init__(self, method_state: MockMethodState, *args, **kwargs):
        self._method_state = method_state
        self._args = args
        self._kwargs = kwargs

    def then_return(self, result: R) -> None:
        self._method_state.set_response(result, *self._args, **self._kwargs)

    def then_raise(self, error: Exception) -> None:
        self._method_state.set_error_response(error, *self._args, **self._kwargs)

    def then_return_many(self, results: List[R], loop: bool = False) -> None:
        self._method_state.set_response_many(results, loop, *self._args, **self._kwargs)
