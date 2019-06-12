from typing import TypeVar, Callable

from typemock._mock import (
    _tmock,
    _when
)
from typemock._verify import _verify
from typemock.api import TypeSafety

T = TypeVar('T')
R = TypeVar('R')

tmock: Callable[[T, TypeSafety], T] = _tmock
when = _when
verify: Callable[[T], T] = _verify
