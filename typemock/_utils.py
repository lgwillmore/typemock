import inspect
import logging
from types import FunctionType
from typing import List, Type, Dict, Optional, TypeVar

T = TypeVar('T')


class Blank:
    pass


class FunctionEntry:

    def __init__(self, name: str, func: FunctionType):
        self.name = name
        self.func = func


class AttributeEntry:
    def __init__(self, name: str, initial_value, type_hint: Type):
        self.name = name
        self.initial_value = initial_value
        self.type_hint = type_hint


def _is_magic(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def _is_private(name: str) -> bool:
    return name.startswith("_")


def methods(cls, include_private=False) -> List[FunctionEntry]:
    function_entries = []
    for name, func in cls.__dict__.items():
        if isinstance(func, FunctionType):
            if _is_magic(name):
                continue
            elif name.startswith("_"):
                if include_private:
                    function_entries.append(FunctionEntry(
                        name=name,
                        func=func
                    ))
            else:
                function_entries.append(FunctionEntry(
                    name=name,
                    func=func
                ))
    return function_entries


def attributes(cls, instance=None) -> List[AttributeEntry]:
    entries: Dict[str, AttributeEntry] = {}
    annotations = cls.__dict__.get("__annotations__", {})
    init_signature = inspect.getfullargspec(cls.__init__)
    class_attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
    class_attributes = [a for a in class_attributes if not _is_magic(a[0]) and not _is_private(a[0])]
    for attribute in class_attributes:
        name = attribute[0]
        type_hint = annotations.get(name, init_signature.annotations.get(name, Blank))
        entries[name] = AttributeEntry(
            name=name,
            initial_value=attribute[1],
            type_hint=type_hint
        )
    instance_attributes = inspect.getmembers(instance, lambda a: not (inspect.isroutine(a)))
    instance_attributes = [a for a in instance_attributes if not _is_magic(a[0]) and not _is_private(a[0])]
    for attribute in instance_attributes:
        name = attribute[0]
        if name in entries:
            pass
        else:
            type_hint = init_signature.annotations.get(attribute[0], Blank)
            entries[name] = AttributeEntry(
                name=name,
                initial_value=attribute[1],
                type_hint=type_hint
            )

    return list(entries.values())


def bind(instance, func, as_name=None):
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method


def typemock_logger():
    return logging.getLogger("typemock")


def try_instantiate_class(cls: Type[T]) -> Optional[T]:
    init_signature = inspect.getfullargspec(cls.__init__)
    stub_args = tuple([None for _ in range(1, len(init_signature.args))])
    try:
        if len(stub_args) > 0:
            return cls(*stub_args)  # type: ignore
        else:
            return cls()
    except Exception:
        typemock_logger().warning(
            "Could not instantiate instance of {}. Instance attributes will not be available for mocking".format(cls)
        )
        return None
