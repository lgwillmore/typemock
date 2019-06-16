from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from typemock.api import NoBehaviourSpecifiedError

T = TypeVar('T')
R = TypeVar('R')


class Responder(ABC, Generic[R]):
    """
    Base Responder for a given set of args. Allows for implementation of different logic to get the response.
    """

    @abstractmethod
    def response(self, *args, **kwargs) -> R:
        pass


class ResponderBasic(Generic[R], Responder[R]):

    def __init__(self, response: R):
        self._response = response

    def response(self, *args, **kwargs) -> R:
        return self._response


class ResponderRaise(Responder[Exception]):

    def __init__(self, error: Exception):
        self._error = error

    def response(self, *args, **kwargs) -> R:
        raise self._error


class ResponderMany(Generic[R], Responder[R]):

    def __init__(self, responses: List[R], loop: bool):
        self._responses = responses
        self._loop = loop
        self._index = 0

    def response(self, *args, **kwargs) -> R:
        if self._index > len(self._responses) - 1:
            if self._loop:
                self._index = 0
            else:
                raise NoBehaviourSpecifiedError("No more responses. Do you want to loop through many responses?")
        response = self._responses[self._index]
        self._index += 1
        return response
