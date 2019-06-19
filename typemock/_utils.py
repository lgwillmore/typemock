import inspect
import logging
import types
import typing
from types import FunctionType
from typing import List, Type, Dict, Optional, TypeVar, Union, Any

T = TypeVar('T')


class Blank:
    pass


def typemock_logger():
    return logging.getLogger("typemock")


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


def is_property(name: str, thing: Union[Type[T], T]) -> bool:
    if inspect.isclass(thing):
        return isinstance(thing.__dict__[name], property)
    else:
        return isinstance(thing.__class__.__dict__[name], property)


def get_property(name: str, thing: Union[Type[T], T]) -> property:
    if inspect.isclass(thing):
        return thing.__dict__[name]
    else:
        return thing.__class__.__dict__[name]


def getmembers(object, predicate=None):
    """
    Modified implementation of inspect.get_members to handle retrieval of values for members which throw an error.

    Args:
        object:
        predicate:

    Returns:

    """
    if inspect.isclass(object):
        mro = (object,) + inspect.getmro(object)
    else:
        mro = ()
    results = []
    processed = set()
    names = dir(object)
    # :dd any DynamicClassAttributes to the list of names if object is a class;
    # this may result in duplicate entries if, for example, a virtual
    # attribute with the same name as a DynamicClassAttribute exists
    try:
        for base in object.__bases__:
            for k, v in base.__dict__.items():
                if isinstance(v, types.DynamicClassAttribute):
                    names.append(k)
    except AttributeError:
        pass
    for key in names:
        # First try to get the value via getattr.  Some descriptors don't
        # like calling their __get__ (see bug #1785), so fall back to
        # looking in the __dict__.
        try:
            value = getattr(object, key)
            # handle the duplicate key
            if key in processed:
                raise AttributeError
        except AttributeError:
            for base in mro:
                if key in base.__dict__:
                    value = base.__dict__[key]
                    break
            else:
                # could be a (currently) missing slot member, or a buggy
                # __dir__; discard and move on
                continue
        except Exception:
            if is_property(key, object):
                value = get_property(key, object)
            else:
                typemock_logger().warning(
                    "Could not determine type of member {}. Will not be available for mocking.".format(
                        key
                    )
                )
                continue
        if not predicate or predicate(value):
            results.append((key, value))
        processed.add(key)
    results.sort(key=lambda pair: pair[0])
    return results


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


def _type_hint_for_attribute_from_value(current_hint, value) -> Any:
    if isinstance(value, property):
        return typing.get_type_hints(value.fget)["return"]
    else:
        return current_hint


def attributes(cls, instance=None) -> List[AttributeEntry]:
    entries: Dict[str, AttributeEntry] = {}
    annotations = cls.__dict__.get("__annotations__", {})
    init_signature = inspect.getfullargspec(cls.__init__)
    class_attributes = getmembers(cls, lambda a: not (inspect.isroutine(a)))
    class_attributes = [a for a in class_attributes if not _is_magic(a[0]) and not _is_private(a[0])]
    for attribute in class_attributes:
        name = attribute[0]
        value = attribute[1]
        type_hint = annotations.get(name, init_signature.annotations.get(name, Blank))
        if type_hint is Blank:
            type_hint = _type_hint_for_attribute_from_value(type_hint, value)
        entries[name] = AttributeEntry(
            name=name,
            initial_value=value,
            type_hint=type_hint
        )
    instance_attributes = getmembers(instance, lambda a: not (inspect.isroutine(a)))
    instance_attributes = [a for a in instance_attributes if not _is_magic(a[0]) and not _is_private(a[0])]
    for attribute in instance_attributes:
        name = attribute[0]
        value = attribute[1]
        if name in entries:
            pass
        else:
            type_hint = init_signature.annotations.get(attribute[0], Blank)
            if type_hint is Blank:
                type_hint = _type_hint_for_attribute_from_value(type_hint, value)
            entries[name] = AttributeEntry(
                name=name,
                initial_value=value,
                type_hint=type_hint
            )

    return list(entries.values())


def bind(instance, func, as_name=None):
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method


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
