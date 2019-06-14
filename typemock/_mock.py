import inspect
from abc import ABC, abstractmethod
from inspect import Signature
from types import FunctionType
from typing import TypeVar, Generic, Type, Callable, List, Tuple, Any, Dict, cast

from typemock._safety import validate_class_type_hints
from typemock._utils import methods, bind, attributes, Blank
from typemock.api import MockTypeSafetyError, NoBehaviourSpecifiedError, ResponseBuilder, TypeSafety, MockingError
from typemock.match import Matcher

T = TypeVar('T')
R = TypeVar('R')

OrderedCallValues = Tuple[Tuple[str, Any], ...]


class CallCount:

    def __init__(self, call: OrderedCallValues, count: int, other_call_count: int):
        self.call = call
        self.count = count
        self.other_call_count = other_call_count


def _has_matchers(call: OrderedCallValues) -> bool:
    for call_param in call:
        if isinstance(call_param[1], Matcher):
            return True
    return False


class Responder(ABC, Generic[R]):
    """
    Base Responder for a method call. Allows for implementation of different logic to get the response.
    """

    @abstractmethod
    def response(self, *args, **kwargs) -> R:
        pass


class ResponderBasic(Generic[R], Responder[R]):

    def __init__(self, response: R):
        self._response = response

    def response(self, *args, **kwargs) -> R:
        return self._response


class ResponderRaise(Responder[Exception]):

    def __init__(self, error: Exception):
        self._error = error

    def response(self, *args, **kwargs) -> R:
        raise self._error


class ResponderMany(Generic[R], Responder[R]):

    def __init__(self, responses: List[R], loop: bool):
        self._responses = responses
        self._loop = loop
        self._index = 0

    def response(self, *args, **kwargs) -> R:
        if self._index > len(self._responses) - 1:
            if self._loop:
                self._index = 0
            else:
                raise NoBehaviourSpecifiedError("No more responses. Do you want to loop through many responses?")
        response = self._responses[self._index]
        self._index += 1
        return response


class _MockMethodState(Generic[R]):

    def __init__(
            self,
            name: str,
            signature: Signature,
            func: FunctionType,
            type_safety: TypeSafety
    ):
        self.name = name
        self._func = func
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
        args_dict = {}
        for i in range(1, len(args)):
            arg = args[i]
            args_dict[self._arg_index_to_arg_name[i]] = arg
        for key, value in kwargs.items():
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
        func_annotations = self._func.__annotations__
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
        if _has_matchers(key):
            self._matcher_responses[key] = ResponderBasic(response)
        else:
            self._responses[key] = ResponderBasic(response)

    def set_response_many(self, results: List[R], loop: bool, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        self._check_key_type_safety(key)
        for response in results:
            self._validate_return(response)
        if _has_matchers(key):
            self._matcher_responses[key] = ResponderMany(results, loop)
        else:
            self._responses[key] = ResponderMany(results, loop)

    def set_error_response(self, error: Exception, *args, **kwargs):
        key = self._ordered_call(*args, **kwargs)
        self._check_key_type_safety(key)
        if _has_matchers(key):
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
        func_annotations = self._func.__annotations__
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


def _mock_method(state: _MockMethodState) -> Callable:
    if inspect.iscoroutinefunction(state._func):
        async def method_mock(*args, **kwargs):
            if state.is_open():
                return _MethodResponseBuilder(state, *args, **kwargs)
            else:
                return state.response_for(*args, **kwargs)

        return method_mock
    else:
        def method_mock(*args, **kwargs):
            if state.is_open():
                return _MethodResponseBuilder(state, *args, **kwargs)
            else:
                return state.response_for(*args, **kwargs)

        return method_mock


class CalledSetRecord:

    def __init__(self, call: Any, count: int, other_call_count: int):
        self.call = call
        self.count = count
        self.other_call_count = other_call_count


class _MockAttributeState(Generic[R]):

    def __init__(self, name: str, initial_value: R, type_hint: Type):
        self.name = name
        self.type_hint = type_hint
        self._responder: Responder = ResponderBasic(initial_value)
        self._call_count = 0
        self._set_calls: List[R] = []

    def _validate_return(self, response: R):
        if not isinstance(self.type_hint, Blank):
            if not isinstance(response, self.type_hint):
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

    def response(self) -> R:
        self._call_count += 1
        return self._responder.response()

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


class _MockObject(Generic[T], object):

    def __init__(self, mocked_class: Type[T], type_safety: TypeSafety):
        validate_class_type_hints(mocked_class, type_safety)
        self._mocked_class = mocked_class
        self._mock_method_states: List[_MockMethodState] = []
        self._mock_attribute_states: Dict[str, _MockAttributeState] = {}
        self._open = False

        # Set up method mocks
        for func_entry in methods(mocked_class):
            sig = inspect.signature(func_entry.func)
            method_state: _MockMethodState = _MockMethodState(
                name=func_entry.name,
                signature=sig,
                func=func_entry.func,
                type_safety=type_safety
            )
            self._mock_method_states.append(method_state)
            mock_method = _mock_method(method_state)
            bind(self, mock_method, func_entry.name)

        # Set up attribute mocks
        attributes_entries = attributes(mocked_class)
        for attribute_entry in attributes_entries:
            attribute_state = _MockAttributeState(
                name=attribute_entry.name,
                initial_value=attribute_entry.initial_value,
                type_hint=attribute_entry.type_hint
            )
            self._mock_attribute_states[attribute_entry.name] = attribute_state

    def __getattribute__(self, item: str):
        if item.startswith("_") or item in {"is_open"}:
            return object.__getattribute__(self, item)
        if self.is_open():
            if item in self._mock_attribute_states:
                state = self._mock_attribute_states[item]
                return _AttributeResponseBuilder(state)
            else:
                return object.__getattribute__(self, item)
        else:
            if item in self._mock_attribute_states:
                state = self._mock_attribute_states[item]
                return state.response()
            else:
                return object.__getattribute__(self, item)

    def __setattr__(self, key, item):
        if hasattr(self, "_mock_attribute_states"):
            mock_attribute_states = self._mock_attribute_states
            if key in mock_attribute_states:
                if self.is_open():
                    raise Exception("Cannot mock behaviour of setting an attribute at this time")
                state = mock_attribute_states[key]
                state.called_set_with(item)
        object.__setattr__(self, key, item)

    @property  # type: ignore
    def __class__(self):
        return self._mocked_class

    def __enter__(self):
        self._open = True
        for method_state in self._mock_method_states:
            method_state.open_for_setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._open = False
        for method_state in self._mock_method_states:
            method_state.close_setup()

    def is_open(self) -> bool:
        return self._open


class _MethodResponseBuilder(Generic[R], ResponseBuilder[R]):

    def __init__(self, method_state: _MockMethodState, *args, **kwargs):
        self._method_state = method_state
        self._args = args
        self._kwargs = kwargs

    def then_return(self, result: R) -> None:
        self._method_state.set_response(result, *self._args, **self._kwargs)

    def then_raise(self, error: Exception) -> None:
        self._method_state.set_error_response(error, *self._args, **self._kwargs)

    def then_return_many(self, results: List[R], loop: bool = False) -> None:
        self._method_state.set_response_many(results, loop, *self._args, **self._kwargs)


class _AttributeResponseBuilder(Generic[R], ResponseBuilder[R]):

    def __init__(self, attribute_state: _MockAttributeState):
        self._attribute_state = attribute_state

    def then_return(self, result: R) -> None:
        self._attribute_state.set_response(result)

    def then_raise(self, error: Exception) -> None:
        self._attribute_state.set_error_response(error)

    def then_return_many(self, results: List[R], loop: bool = False) -> None:
        self._attribute_state.set_response_many(results, loop)


def _tmock(clazz: Type[T], type_safety: TypeSafety = TypeSafety.STRICT) -> T:
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
    return cast(T, _MockObject(clazz, type_safety))


def _when(mock_call_result: T) -> ResponseBuilder[T]:
    if not isinstance(mock_call_result, ResponseBuilder):
        raise MockingError(
            "Did not receive a response builder. Are you trying to specify behaviour outside of the mock context?"
        )
    return cast(ResponseBuilder[T], mock_call_result)
