from abc import ABC, abstractmethod
from enum import Enum
from typing import TypeVar, List, Generic

T = TypeVar('T')
R = TypeVar('R')


class ResponseBuilder(ABC, Generic[R]):

    @abstractmethod
    def then_return(self, result: R) -> None:
        """
        Sets the behaviour of the mock to return the given response.

        Args:
            result:

        """

    @abstractmethod
    def then_raise(self, error: Exception) -> None:
        """
        Sets the behaviour of the mock to raise the given Exception.

        Args:
            error:

        """

    @abstractmethod
    def then_return_many(self, results: List[R], loop: bool = False) -> None:
        """
        Sets the behaviour of the mock to iterate through a series of results on each successive call.

        Args:
            results:

                The results to return with each successive call.

            loop:

                If False, an error will be raised when responses are exhausted. If True, responses will start from
                first response again.

        """


class TypeSafety(Enum):
    STRICT = 1  # Everything must be type hinted
    NO_RETURN_IS_NONE_RETURN = 2  # Everything type hinted, but no returns are interpreted as None returns
    RELAXED = 3  # Enforce type safety where there are type hints.


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


class MissingTypeHintsError(Exception):
    pass


class MockTypeSafetyError(Exception):
    pass


class NoBehaviourSpecifiedError(Exception):
    pass


class VerifyError(Exception):
    pass


class MockingError(Exception):
    pass
