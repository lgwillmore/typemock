import inspect
from typing import List

from typemock.utils import methods


class MemberType:
    ARG: str = "arg"
    ATTRIBUTE: str = "attribute"
    RETURN: str = "return"


class MissingHint:

    def __init__(self, path: List[str], member_type: str):
        self.path = path
        self.member_type = member_type

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.member_type == other.member_type and self.path == other.path

    def __repr__(self):
        return "MissingHint(path={path}, member_type={member_type})".format(
            path=self.path,
            member_type=self.member_type
        )


def _validate_method_annotations(clazz, missing: List[MissingHint]):
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
            if "return" not in annotations:
                missing.append(
                    MissingHint(
                        path=[name],
                        member_type=MemberType.RETURN
                    )
                )


def _validate_attributes(clazz, missing: List[MissingHint]):
    pass


def get_missing_class_type_hints(clazz) -> List[MissingHint]:
    missing = []
    _validate_attributes(clazz, missing)
    _validate_method_annotations(clazz, missing)
    return missing


def validate_class_type_hints(clazz) -> List[MissingHint]:
    missing = get_missing_class_type_hints(clazz)
    if len(missing) > 0:
        raise MissingTypeHintsError(
            "{} has missing type hints.".format(clazz),
            missing
        )


class MissingTypeHintsError(Exception):
    pass


class MockTypeSafetyError(Exception):
    pass
