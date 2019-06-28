import inspect
from typing import List, Type, TypeVar, Optional

from typemock._utils import methods, attributes, Blank, try_instantiate_class
from typemock.api import MemberType, MissingHint, MissingTypeHintsError, TypeSafety, TypeSafetyConfig

T = TypeVar('T')


def _validate_method_annotations(clazz: Type[T], type_safety: TypeSafetyConfig, missing: List[MissingHint]):
    for func_entry in methods(clazz):
        func = func_entry.func
        name = func_entry.name
        sig = inspect.signature(func_entry.func)
        if len(sig.parameters) > 0:
            annotations = func.__annotations__
            if not type_safety.relax_method_arg_types:
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

            if not type_safety.no_return_is_none_return and "return" not in annotations:
                missing.append(
                    MissingHint(
                        path=[name],
                        member_type=MemberType.RETURN
                    )
                )


def _validate_attributes(
        clazz: Type[T],
        instance: Optional[T],
        type_safety: TypeSafetyConfig,
        missing: List[MissingHint]
):
    if type_safety.relax_attribute_types:
        return
    for attribute_entry in attributes(clazz, instance):
        if attribute_entry.type_hint is Blank:
            missing.append(
                MissingHint(
                    path=[attribute_entry.name],
                    member_type=MemberType.ATTRIBUTE
                )
            )


def get_missing_class_type_hints(
        clazz: Type[T],
        instance: Optional[T],
        type_safety: TypeSafetyConfig
) -> List[MissingHint]:
    missing: List[MissingHint] = []
    _validate_attributes(clazz, instance, type_safety, missing)
    _validate_method_annotations(clazz, type_safety, missing)
    return missing


def validate_class_type_hints(
        clazz: Type[T],
        instance: Optional[T] = None,
        type_safety: TypeSafetyConfig = TypeSafety.STRICT
) -> None:
    """
    Args:
        clazz:
        instance:
        type_safety:

    Raises:

        MissingTypeHintsError

    """
    instance = instance or try_instantiate_class(clazz)
    missing = get_missing_class_type_hints(clazz, instance, type_safety)
    if len(missing) > 0:
        raise MissingTypeHintsError(
            "{} has missing type hints.".format(clazz),
            missing
        )
