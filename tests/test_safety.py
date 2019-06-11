from unittest import TestCase

from typemock import tmock, when
from typemock.api import MemberType, MissingHint, MissingTypeHintsError, MockTypeSafetyError


class ClassWithMultipleUnHintedThings:

    def __init__(self):
        # We do not care about type hints for magic methods
        pass

    def _some_private_function(self):
        # We do not care about type hints for private methods
        pass

    def good_method_with_args_and_return(self, number: int) -> str:
        pass

    def good_method_with_no_args_and_return(self) -> str:
        pass

    def method_with_missing_arg_hint(self, something, something_else: bool) -> None:
        pass

    def method_with_missing_return_type(self):
        pass


class MyThing:

    def return_a_str(self) -> str:
        pass

    def convert_int_to_str(self, number: int) -> str:
        pass

    def multiple_arg(self, prefix: str, number: int) -> str:
        pass

    def do_something_with_side_effects(self) -> None:
        pass


class TestSafety(TestCase):

    def test_validate_class_type_hints(self):
        expected_missing_type_hints = [
            MissingHint(["method_with_missing_arg_hint", "something"], MemberType.ARG),
            MissingHint(["method_with_missing_return_type"], MemberType.RETURN),
        ]

        with self.assertRaises(MissingTypeHintsError) as error:
            tmock(ClassWithMultipleUnHintedThings)
        actual_missing_type_hints = error.exception.args[1]

        self.assertEqual(expected_missing_type_hints, actual_missing_type_hints)

    def test_try_to_specify_non_type_safe_argument_matching__simple_type(self):
        with self.assertRaises(MockTypeSafetyError):
            with tmock(MyThing) as my_thing_mock:
                when(my_thing_mock.convert_int_to_str("not an int")).then_return("another string")

    def test_try_to_specify_non_type_safe_return_type__simple_type(self):
        with self.assertRaises(MockTypeSafetyError):
            with tmock(MyThing) as my_thing_mock:
                when(my_thing_mock.convert_int_to_str(1)).then_return(2)

    def test_try_to_specify_non_type_safe_return_type__simple_type__return_many(self):
        with self.assertRaises(MockTypeSafetyError):
            with tmock(MyThing) as my_thing_mock:
                when(my_thing_mock.convert_int_to_str(1)).then_return_many(["okay", 1])

    # TODO: Attribute and Property type safety. Recursive type safety for nested objects (only their attributes and properties).
