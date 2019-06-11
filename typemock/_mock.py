import inspect
from abc import ABC, abstractmethod
from inspect import Signature
from types import FunctionType
from typing import TypeVar, Generic, Type, Callable, List, Tuple, Any, Dict

from typemock._safety import validate_class_type_hints
from typemock._utils import methods, bind
from typemock.api import MockTypeSafetyError, NoBehaviourSpecifiedError, ResponseBuilder, TypeSafety

T = TypeVar('T')
R = TypeVar('R')

OrderedCallValues = Tuple[Tuple[str, Any], ...]


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


class ResponderRaise(Responder[Type[Exception]]):

    def __init__(self, error: Type[Exception]):
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
        self._responses: Dict[OrderedCallValues, Responder[R]] = {}
        self._open = False
        self._arg_index_to_arg_name = {}
        self._arg_name_to_parameter = {}
        self._call_record: List[OrderedCallValues] = []
        i = 0
        for name, param in signature.parameters.items():
            self._arg_index_to_arg_name[i] = name
            self._arg_name_to_parameter[name] = param
            i += 1

    def _key(self, *args, **kwargs) -> OrderedCallValues:
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
            ordered_key_values.append((name, args_dict[name]))
        key = tuple(ordered_key_values)
        return key

    def response_for(self, *args, **kwargs) -> R:
        key = self._key(*args, **kwargs)
        self._call_record.append(key)
        if key in self._responses:
            return self._responses[key].response(*args, *kwargs)
        else:
            raise NoBehaviourSpecifiedError()

    def call_count_for(self, *args, **kwargs) -> int:
        count = 0
        expected_call = self._key(*args, **kwargs)
        for call in self._call_record:
            if call == expected_call:
                count += 1
        return count

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
        key = self._key(*args, **kwargs)
        self._check_key_type_safety(key)
        self._validate_return(response)
        self._responses[key] = ResponderBasic(response)

    def set_response_many(self, results: List[R], loop: bool, *args, **kwargs):
        key = self._key(*args, **kwargs)
        self._check_key_type_safety(key)
        for response in results:
            self._validate_return(response)
        self._responses[key] = ResponderMany(results, loop)

    def set_error_response(self, error: Type[Exception], *args, **kwargs):
        key = self._key(*args, **kwargs)
        self._check_key_type_safety(key)
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
            if arg_name in func_annotations:
                arg_type = func_annotations[arg_name]
                if not isinstance(arg_value, arg_type):
                    raise MockTypeSafetyError("Method: {} Arg: {} must be of type:{}".format(
                        self.name,
                        arg_name,
                        arg_type
                    ))


def _mock_method(state: _MockMethodState) -> Callable:
    def method_mock(*args, **kwargs):
        if state.is_open():
            return _MockingResponseBuilder(state, *args, **kwargs)
        else:
            return state.response_for(*args, **kwargs)

    return method_mock


class _MockObject(Generic[T]):

    def __init__(self, mocked_class: Type[T], type_safety: TypeSafety):
        validate_class_type_hints(mocked_class, type_safety)
        self._mocked_class = mocked_class
        self._mock_method_states: List[_MockMethodState] = []
        self._open = False
        for func_entry in methods(mocked_class):
            sig = inspect.signature(func_entry.func)
            method_state = _MockMethodState(
                name=func_entry.name,
                signature=sig,
                func=func_entry.func,
                type_safety=type_safety
            )
            self._mock_method_states.append(method_state)
            mock_method = _mock_method(method_state)
            bind(self, mock_method, func_entry.name)

    @property
    def __class__(self):
        return self._mocked_class

    def __enter__(self):
        self.open_for_setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_setup()

    def __instancecheck__(self, instance):
        return type(instance) == type(self._mocked_class)

    def open_for_setup(self):
        self._open = True
        for method_state in self._mock_method_states:
            method_state.open_for_setup()

    def close_setup(self):
        self._open = False
        for method_state in self._mock_method_states:
            method_state.close_setup()

    def is_open(self) -> bool:
        return self._open


class _MockingResponseBuilder(Generic[R], ResponseBuilder[R]):

    def __init__(self, method_state: _MockMethodState, *args, **kwargs):
        self._method_state = method_state
        self._args = args
        self._kwargs = kwargs

    def then_return(self, result: R) -> None:
        self._method_state.set_response(result, *self._args, **self._kwargs)

    def then_raise(self, error: Type[Exception]) -> None:
        self._method_state.set_error_response(error, *self._args, **self._kwargs)

    def then_return_many(self, results: List[R], loop: bool = False) -> None:
        self._method_state.set_response_many(results, loop, *self._args, **self._kwargs)


def tmock(clazz: Type[T], type_safety: TypeSafety = TypeSafety.STRICT) -> T:
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
    return _MockObject(clazz, type_safety)


def when(mock_function_call_result: T) -> _MockingResponseBuilder[T]:
    return mock_function_call_result
