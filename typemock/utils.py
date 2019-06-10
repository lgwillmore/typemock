from types import FunctionType
from typing import List


class FunctionEntry:

    def __init__(self, name: str, func: FunctionType):
        self.name = name
        self.func = func


def methods(cls) -> List[FunctionEntry]:
    return [FunctionEntry(x, y) for x, y in cls.__dict__.items() if isinstance(y, FunctionType)]


def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the
    instance as the first argument, i.e. "self".
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method
