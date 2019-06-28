from abc import ABC, abstractmethod
from typing import TypeVar, List, Generic, Callable

T = TypeVar('T')
R = TypeVar('R')

DoFunction = Callable[..., R]


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

    @abstractmethod
    def then_do(self, do_function: DoFunction) -> None:
        """
        Sets the behaviour of the mock to return the result of calling the do_function with the args provided.

        Args:

            do_function:

        Returns:

            result:

                Returns whatever he do_function returns.
                This will be type checked to see that it matches the return type that it is mocking.

        """


class TypeSafetyConfig:

    def __init__(
            self,
            no_return_is_none_return: bool = False,
            relax_method_arg_types: bool = False,
            relax_attribute_types: bool = False,
    ):
        self.no_return_is_none_return = no_return_is_none_return
        self.relax_method_arg_types = relax_method_arg_types
        self.relax_attribute_types = relax_attribute_types


class TypeSafety:
    # Everything must be type hinted
    STRICT: TypeSafetyConfig = TypeSafetyConfig()

    # Everything type hinted, but no returns are interpreted as None returns
    NO_RETURN_IS_NONE_RETURN: TypeSafetyConfig = TypeSafetyConfig(
        no_return_is_none_return=True
    )

    # Enforce type safety where there are type hints.
    RELAXED: TypeSafetyConfig = TypeSafetyConfig(
        no_return_is_none_return=True,
        relax_attribute_types=True,
        relax_method_arg_types=True
    )

    @classmethod
    def all(cls):
        return [
            cls.STRICT,
            cls.RELAXED,
            cls.NO_RETURN_IS_NONE_RETURN
        ]


class MemberType:
    ARG: str = "arg"
    ATTRIBUTE: str = "attribute"
    RETURN: str = "return"


class MissingHint:
    """
    Describes the path to a missing type hint annotation.
    """

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
