from unittest import TestCase

from typemock.safety import validate_class_type_hints, MissingHint, MemberType, MissingTypeHintsError


class ClassWithMultipleUnHintedThings:

    def good_method_with_args_and_return(self, number: int) -> str:
        pass

    def good_method_with_no_args_and_return(self) -> str:
        pass

    def method_with_missing_arg_hint(self, something, something_else: bool) -> None:
        pass

    def method_with_missing_return_type(self):
        pass


class TestSafety(TestCase):

    def test_validate_class_type_hints(self):
        expected_missing_type_hints = [
            MissingHint(["method_with_missing_arg_hint", "something"], MemberType.ARG),
            MissingHint(["method_with_missing_return_type"], MemberType.RETURN),
        ]

        with self.assertRaises(MissingTypeHintsError) as error:
            validate_class_type_hints(ClassWithMultipleUnHintedThings)
        actual_missing_type_hints = error.exception.args[1]

        self.assertEqual(expected_missing_type_hints, actual_missing_type_hints)

    # TODO: Attribute and Property type safety. Recursive type safety for nested objects (only their attributes and properties).



