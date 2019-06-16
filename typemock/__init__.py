from typing import TypeVar, Type, Union

from typemock._mock import (
    _tmock,
    _when
)
from typemock._verify import _verify
from typemock.api import TypeSafety, ResponseBuilder

T = TypeVar('T')
R = TypeVar('R')


def tmock(clazz: Union[Type[T], T], type_safety: TypeSafety = TypeSafety.STRICT) -> T:
    return _tmock(clazz=clazz, type_safety=type_safety)


def when(mock_call_result: R) -> ResponseBuilder[R]:
    return _when(mock_call_result=mock_call_result)


def verify(mock: T, exactly: int = -1) -> T:
    return _verify(mock=mock, exactly=exactly)
