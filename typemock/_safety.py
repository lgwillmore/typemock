import inspect
from typing import List, Type, TypeVar

from typemock._utils import methods, attributes
from typemock.api import MemberType, MissingHint, MissingTypeHintsError, TypeSafety

T = TypeVar('T')


def _validate_method_annotations(clazz: Type[T], type_safety: TypeSafety, missing: List[MissingHint]):
    for func_entry in methods(clazz):
        func = func_entry.func
        name = func_entry.name
        sig = inspect.signature(func_entry.func)
        if len(sig.parameters) > 0:
            annotations = func.__annotations__
            for param_name in sig.parameters:
                if param_name == "self":
                    continue
                else:
                    if param_name not in annotations:
                        missing.append(
                            MissingHint(
                                path=[name, param_name],
                                member_type=MemberType.ARG
                            )
                        )

            if type_safety != TypeSafety.NO_RETURN_IS_NONE_RETURN and "return" not in annotations:
                missing.append(
                    MissingHint(
                        path=[name],
                        member_type=MemberType.RETURN
                    )
                )


def _validate_attributes(clazz: Type[T], type_safety: TypeSafety, missing: List[MissingHint]):
    class_annotations = clazz.__dict__.get("__annotations__", {})
    for attribute_entry in attributes(clazz):
        if attribute_entry.name not in class_annotations:
            missing.append(
                MissingHint(
                    path=[attribute_entry.name],
                    member_type=MemberType.ATTRIBUTE
                )
            )


def get_missing_class_type_hints(clazz: Type[T], type_safety: TypeSafety) -> List[MissingHint]:
    missing: List[MissingHint] = []
    _validate_attributes(clazz, type_safety, missing)
    _validate_method_annotations(clazz, type_safety, missing)
    return missing


def validate_class_type_hints(clazz: Type[T], type_safety: TypeSafety) -> None:
    """
    Args:
        clazz:
        type_safety:

    Raises:

        MissingTypeHintsError

    """
    if type_safety == TypeSafety.RELAXED:
        return
    missing = get_missing_class_type_hints(clazz, type_safety)
    if len(missing) > 0:
        raise MissingTypeHintsError(
            "{} has missing type hints.".format(clazz),
            missing
        )
