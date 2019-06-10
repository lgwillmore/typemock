import inspect
from inspect import Signature
from types import FunctionType
from typing import TypeVar, Generic, Type, Callable, List, Tuple, Any, Dict

from typemock.safety import validate_class_type_hints, MockTypeSafetyError
from typemock.utils import methods, bind

T = TypeVar('T')
R = TypeVar('R')

OrderedCallValues = Tuple[Tuple[str, Any], ...]


class MockMethodState(Generic[R]):

    def __init__(self, name: str, signature: Signature, func: FunctionType):
        self.name = name
        self._func = func
        self._signature = signature
        self._responses: Dict[OrderedCallValues, R] = {}
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
            return self._responses[key]
        else:
            raise NoBehaviourSpecifiedError()

    def call_count_for(self, *args, **kwargs) -> int:
        count = 0
        expected_call = self._key(*args, **kwargs)
        for call in self._call_record:
            if call == expected_call:
                count += 1
        return count

    def set_response(self, response: R, *args, **kwargs):
        key = self._key(*args, **kwargs)
        func_annotations = self._func.__annotations__
        for call_arg in key:
            arg_name = call_arg[0]
            arg_value = call_arg[1]
            arg_type = func_annotations[arg_name]
            if not isinstance(arg_value, arg_type):
                raise MockTypeSafetyError("Method: {} Arg: {} must be of type:{}".format(
                    self.name,
                    arg_name,
                    arg_type
                ))
        return_type = func_annotations["return"]
        if not isinstance(response, return_type):
            raise MockTypeSafetyError("Method: {} return must be of type:{}".format(
                self.name,
                return_type,
            ))
        self._responses[key] = response

    def open_for_setup(self):
        self._open = True

    def close_setup(self):
        self._open = False

    def is_open(self) -> bool:
        return self._open


class MockingResponseBuilder(Generic[T]):

    def __init__(self, method_state: MockMethodState, *args, **kwargs):
        self._method_state = method_state
        self._args = args
        self._kwargs = kwargs

    def then_return(self, result: T):
        self._method_state.set_response(result, *self._args, **self._kwargs)


def _mock_method(state: MockMethodState) -> Callable:
    def method_mock(*args, **kwargs):
        if state.is_open():
            return MockingResponseBuilder(state, *args, **kwargs)
        else:
            return state.response_for(*args, **kwargs)

    return method_mock


class MockObject(Generic[T]):

    def __init__(self, mocked_class: Type[T]):
        validate_class_type_hints(mocked_class)
        self._mocked_class = mocked_class
        self._mock_method_states: List[MockMethodState] = []
        self._open = False
        for func_entry in methods(mocked_class):
            sig = inspect.signature(func_entry.func)
            method_state = MockMethodState(
                name=func_entry.name,
                signature=sig,
                func=func_entry.func
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


def tmock(clazz: Type[T]) -> T:
    return MockObject(clazz)


def when(mock_function_call_result: T) -> MockingResponseBuilder[T]:
    return mock_function_call_result


class NoBehaviourSpecifiedError(Exception):
    pass
