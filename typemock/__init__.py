from typing import TypeVar, Callable, Type, Optional

from typemock._mock import (
    _tmock,
    _when
)
from typemock._verify import _verify
from typemock.api import TypeSafety, ResponseBuilder

T = TypeVar('T')
R = TypeVar('R')

tmock: Callable[[Type[T], Optional[TypeSafety]], T] = _tmock
when: Callable[[T], ResponseBuilder[T]] = _when
verify: Callable[[T], T] = _verify
