from abc import ABC, abstractmethod
from typing import TypeVar, Any

T = TypeVar('T')


class Matcher(ABC):

    @abstractmethod
    def matches(self, other: Any) -> bool:
        pass


class MatchAny(Matcher):

    def matches(self, other: Any) -> bool:
        return True

    def __eq__(self, other):
        return True

    def __hash__(self):
        return hash(self.__class__)


_MATCH_ANY = MatchAny()


def anything() -> Matcher:
    """
    Returns a matcher that will match anything. Type safety is still preserved by the mock itself.
    """
    return _MATCH_ANY
