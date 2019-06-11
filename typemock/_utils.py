from types import FunctionType
from typing import List


class FunctionEntry:

    def __init__(self, name: str, func: FunctionType):
        self.name = name
        self.func = func


def _is_magic(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


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


def bind(instance, func, as_name=None):
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method
