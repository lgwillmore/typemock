import inspect
from collections import OrderedDict
from inspect import Signature
from types import FunctionType
from typing import Tuple, Any, Generic, Dict, List, Callable, TypeVar

from typemock._mock.responders import Responder, ResponderBasic, ResponderMany, ResponderRaise, ResponderDo
from typemock._utils import is_type, InefficientUnHashableKeyDict
from typemock.api import MockTypeSafetyError, NoBehaviourSpecifiedError, DoFunction
from typemock.api import TypeSafety, ResponseBuilder
from typemock.match import Matcher

T = TypeVar('T')
R = TypeVar('R')

OrderedCallValues = Tuple[Tuple[str, Any], ...]


class CallCount:

    def __init__(self, call: OrderedCallValues, count: int, other_calls: List[OrderedCallValues]):
        self.call = call
        self.count = count
        self.other_calls = other_calls


_error_invalid_mock_args = """

Invalid arguments for method '{method_name}':

Received args: {attempted_args}, kwargs: {attempted_kwargs}

Expected: {actual_signature}

"""


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
        self._responses: InefficientUnHashableKeyDict[OrderedCallValues, Responder] = InefficientUnHashableKeyDict()
        self._matcher_responses: InefficientUnHashableKeyDict[
            OrderedCallValues, Responder] = InefficientUnHashableKeyDict()
        self._open = False
        self._arg_index_to_arg_name: Dict[int, str] = {}
        self._arg_name_to_parameter: Dict[str, inspect.Parameter] = {}
        self._call_record: List[OrderedCallValues] = []
        i = 0
        for name, param in signature.parameters.items():
            self._arg_index_to_arg_name[i] = name
            self._arg_name_to_parameter[name] = param
            i += 1

    def _populate_defaults(self, ordered_call: OrderedCallValues) -> OrderedCallValues:
        if len(ordered_call) == len(self._arg_index_to_arg_name):
            return ordered_call
        args_dict = {}
        for name, value in ordered_call:
            args_dict[name] = value
        ordered_key_values = []
        for name, param in self._signature.parameters.items():
            if name == "self":
                continue
            value = args_dict.get(
                name,
                self._arg_name_to_parameter[name].default
            )
            ordered_key_values.append((name, value))
        return tuple(ordered_key_values)

    def _ordered_call(self, *args, **kwargs) -> OrderedCallValues:
        try:
            binding = self._signature.bind(*args, **kwargs)
            ordered_call = tuple(binding.arguments.items())[1:]
            ordered_call = self._populate_defaults(ordered_call)
            self._check_key_type_safety(ordered_call)
            return ordered_call
        except TypeError as e:
            raise MockTypeSafetyError(_error_invalid_mock_args.format(
                method_name=self.name,
                attempted_args=args[1:],
                attempted_kwargs=kwargs,
                actual_signature=self._signature
            )) from e

    def response_for(self, *args, **kwargs) -> R:
        key = self._ordered_call(*args, **kwargs)
        self._call_record.append(key)
        if key in self._responses:
            r = self._responses[key].response(*args, **kwargs)
            self._validate_return(r)
            return r
        else:
            for matcher_key, responder in self._matcher_responses.items():
                if matcher_key == key:
                    self._check_key_type_safety(key)
                    r = responder.response(**OrderedDict(key))
                    self._validate_return(r)
                    return r
            raise NoBehaviourSpecifiedError(
                "No behaviour specified for method: {} with args: {}".format(self.name, key)
            )

    def call_count_for(self, *args, **kwargs) -> CallCount:
        other_calls = []
        count = 0
        expected_call = self._ordered_call(*args, **kwargs)
        for call in self._call_record:
            if call == expected_call:
                count += 1
            else:
                other_calls.append(call)
        return CallCount(expected_call, count, other_calls)

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
                elif not is_type(response, return_type):
                    raise MockTypeSafetyError("Method: {} return must be of type:{}".format(
                        self.name,
                        return_type,
                    ))

    def _set_key_to_responder(self, key: OrderedCallValues, responder: Responder):
        if has_matchers(key):
            self._matcher_responses[key] = responder
        else:
            self._responses[key] = responder

    def set_response(self, response: R, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        self._validate_return(response)
        if has_matchers(key):
            self._matcher_responses[key] = ResponderBasic(response)
        else:
            self._responses[key] = ResponderBasic(response)

    def set_response_many(self, results: List[R], loop: bool, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        for response in results:
            self._validate_return(response)
        self._set_key_to_responder(key, ResponderMany(results, loop))

    def set_error_response(self, error: Exception, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        self._set_key_to_responder(key, ResponderRaise(error))

    def set_response_do(self, do_function: DoFunction, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        self._set_key_to_responder(key, ResponderDo(do_function, self._ordered_call))

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
                param = self._arg_name_to_parameter[arg_name]
                arg_type = func_annotations[arg_name]
                if param.kind == inspect.Parameter.VAR_POSITIONAL:
                    arg_type = Tuple[arg_type, ...]  # type: ignore
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    arg_type = Dict[str, arg_type]  # type: ignore
                if not is_type(arg_value, arg_type):
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

    def then_do(self, do_function: DoFunction) -> None:
        self._method_state.set_response_do(do_function, *self._args, **self._kwargs)
