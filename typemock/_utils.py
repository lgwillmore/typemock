import inspect
from types import FunctionType
from typing import List, Type


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


def attributes(cls) -> List[AttributeEntry]:
    entries = []
    annotations = cls.__dict__.get("__annotations__", {})
    attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
    attributes = [a for a in attributes if not _is_magic(a[0]) and not _is_private(a[0])]
    for attribute in attributes:
        type_hint = annotations.get(attribute[0], Blank)
        entries.append(
            AttributeEntry(
                name=attribute[0],
                initial_value=attribute[1],
                type_hint=type_hint
            )
        )
    return entries


def bind(instance, func, as_name=None):
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method
