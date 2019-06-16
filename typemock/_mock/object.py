import inspect
from typing import Generic, Union, Type, cast, Optional, List, Dict, TypeVar

from typemock._mock.attributes import MockAttributeState, AttributeResponseBuilder
from typemock._mock.methods import MockMethodState, mock_method
from typemock._safety import validate_class_type_hints
from typemock._utils import try_instantiate_class, methods, bind, attributes
from typemock.api import TypeSafety

T = TypeVar('T')
R = TypeVar('R')


class MockObject(Generic[T], object):

    def __init__(self, mocked_thing: Union[Type[T], T], type_safety: TypeSafety):
        if not inspect.isclass(mocked_thing):
            mocked_instance: T = cast(T, mocked_thing)
            mocked_class: Type[T] = cast(Type[T], mocked_thing.__class__)
        else:
            mocked_class = mocked_thing  # type: ignore
            mocked_instance: Optional[T] = try_instantiate_class(cast(Type[T], mocked_thing))  # type: ignore
        validate_class_type_hints(
            clazz=mocked_class,
            instance=mocked_instance,
            type_safety=type_safety)
        self._mocked_class = mocked_class
        self._mock_method_states: List[MockMethodState] = []
        self._mock_attribute_states: Dict[str, MockAttributeState] = {}
        self._open = False

        # Set up method mocks
        for func_entry in methods(mocked_class):
            sig = inspect.signature(func_entry.func)
            method_state: MockMethodState = MockMethodState(
                name=func_entry.name,
                signature=sig,
                func=func_entry.func,
                type_safety=type_safety
            )
            self._mock_method_states.append(method_state)
            mocked_method = mock_method(method_state)
            bind(self, mocked_method, func_entry.name)

        # Set up attribute mocks
        attributes_entries = attributes(mocked_class, mocked_instance)
        for attribute_entry in attributes_entries:
            attribute_state = MockAttributeState(
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
                return AttributeResponseBuilder(state)
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

    def __enter__(self) -> T:
        self._open = True
        for method_state in self._mock_method_states:
            method_state.open_for_setup()
        return cast(T, self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._open = False
        for method_state in self._mock_method_states:
            method_state.close_setup()

    def is_open(self) -> bool:
        return self._open
