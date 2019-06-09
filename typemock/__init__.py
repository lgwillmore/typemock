from typing import Callable, Type, TypeVar

from typemock import mock
from typemock.mock import MockingResponseBuilder, MockObject
from typemock.verify import VerifyObject

T = TypeVar('T')
R = TypeVar('R')

tmock: Callable[[Type[T]], T] = mock.tmock

when: Callable[[R], MockingResponseBuilder[R]] = mock.when

verify: Callable[[MockObject[T]], T] = verify.verify
