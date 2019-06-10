from typing import Callable, Type, TypeVar

from typemock import _mock
from typemock import _verify
from typemock import api

T = TypeVar('T')
R = TypeVar('R')

tmock: Callable[[Type[T]], T] = _mock.tmock

when: Callable[[R], api.ResponseBuilder[R]] = _mock.when

verify: Callable[[T], T] = _verify.verify
