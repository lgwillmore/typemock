from unittest import TestCase

from typemock import tmock, when, match
from typemock.api import MemberType, MissingHint, MissingTypeHintsError, MockTypeSafetyError, TypeSafety


class ClassWithNoResponseType:

    def method_with_missing_return_type(self):
        pass


class ClassWithMultipleUnHintedThings:
    a_hinted_attribute: str = "initial_hinted"
    an_unhinted_attribute = "initial_not_hinted"

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
    a_hinted_str_attribute: str = "initial"

    def return_a_str(self) -> str:
        pass

    def convert_int_to_str(self, number: int) -> str:
        pass

    def multiple_arg(self, prefix: str, number: int) -> str:
        pass

    def do_something_with_side_effects(self) -> None:
        pass


class TestSafety(TestCase):

    def test_validate_class_type_hints__strict(self):
        expected_missing_type_hints = [
            MissingHint(["an_unhinted_attribute"], MemberType.ATTRIBUTE),
            MissingHint(["method_with_missing_arg_hint", "something"], MemberType.ARG),
            MissingHint(["method_with_missing_return_type"], MemberType.RETURN),
        ]

        with self.assertRaises(MissingTypeHintsError) as error:
            tmock(ClassWithMultipleUnHintedThings, type_safety=TypeSafety.STRICT)
        actual_missing_type_hints = error.exception.args[1]

        self.assertEqual(expected_missing_type_hints, actual_missing_type_hints)

    def test_validate_class_type_hints__no_return_is_none_return(self):
        expected_missing_type_hints = [
            MissingHint(["an_unhinted_attribute"], MemberType.ATTRIBUTE),
            MissingHint(["method_with_missing_arg_hint", "something"], MemberType.ARG),
        ]

        with self.assertRaises(MissingTypeHintsError) as error:
            tmock(ClassWithMultipleUnHintedThings, type_safety=TypeSafety.NO_RETURN_IS_NONE_RETURN)
        actual_missing_type_hints = error.exception.args[1]

        self.assertEqual(expected_missing_type_hints, actual_missing_type_hints)

    def test_validate_class_type_hints__relaxed(self):
        # Expect no error
        tmock(ClassWithMultipleUnHintedThings, type_safety=TypeSafety.RELAXED)

    def test_try_to_specify_non_type_safe_argument_matching__simple_type(self):
        self._try_to_specify_non_type_safe_argument_matching__simple_type(TypeSafety.STRICT)
        self._try_to_specify_non_type_safe_argument_matching__simple_type(TypeSafety.NO_RETURN_IS_NONE_RETURN)
        self._try_to_specify_non_type_safe_argument_matching__simple_type(TypeSafety.RELAXED)

    def _try_to_specify_non_type_safe_argument_matching__simple_type(self, type_safety: TypeSafety):
        with self.assertRaises(MockTypeSafetyError):
            with tmock(MyThing, type_safety=type_safety) as my_thing_mock:
                when(my_thing_mock.convert_int_to_str("not an int")).then_return("another string")

    def test_try_to_specify_non_type_safe_return_type__simple_type(self):
        self._try_to_specify_non_type_safe_return_type__simple_type(TypeSafety.STRICT)
        self._try_to_specify_non_type_safe_return_type__simple_type(TypeSafety.NO_RETURN_IS_NONE_RETURN)
        self._try_to_specify_non_type_safe_return_type__simple_type(TypeSafety.RELAXED)

    def _try_to_specify_non_type_safe_return_type__simple_type(self, type_safety: TypeSafety):
        # Method
        with self.assertRaises(MockTypeSafetyError):
            with tmock(MyThing, type_safety=type_safety) as my_thing_mock:
                when(my_thing_mock.convert_int_to_str(1)).then_return(2)

        # Attribute get
        with self.assertRaises(MockTypeSafetyError):
            with tmock(MyThing, type_safety=type_safety) as my_thing_mock:
                when(my_thing_mock.a_hinted_str_attribute).then_return(1)

    def test_try_to_specify_non_type_safe_return_type__simple_type__return_many(self):
        self._try_to_specify_non_type_safe_return_type__simple_type__return_many(TypeSafety.STRICT)
        self._try_to_specify_non_type_safe_return_type__simple_type__return_many(TypeSafety.NO_RETURN_IS_NONE_RETURN)
        self._try_to_specify_non_type_safe_return_type__simple_type__return_many(TypeSafety.RELAXED)

    def _try_to_specify_non_type_safe_return_type__simple_type__return_many(self, type_safety: TypeSafety):
        with self.assertRaises(MockTypeSafetyError):
            with tmock(MyThing, type_safety=type_safety) as my_thing_mock:
                when(my_thing_mock.convert_int_to_str(1)).then_return_many(["okay", 1])

    def test_try_to_set_attribute_with_incorrect_type(self):
        self._try_to_set_attribute_with_incorrect_type(TypeSafety.STRICT)
        self._try_to_set_attribute_with_incorrect_type(TypeSafety.NO_RETURN_IS_NONE_RETURN)
        self._try_to_set_attribute_with_incorrect_type(TypeSafety.RELAXED)

    def _try_to_set_attribute_with_incorrect_type(self, type_safety: TypeSafety.STRICT):
        my_thing_mock = tmock(MyThing, type_safety=type_safety)

        # Method
        with self.assertRaises(MockTypeSafetyError):
            my_thing_mock.a_hinted_str_attribute = 1

    # TODO: Recursive type safety for nested objects (only their attributes and properties).


class TestTypeSafetyRelaxed(TestCase):

    def test_specify_behaviour_of_non_hinted_arg(self):
        with tmock(ClassWithMultipleUnHintedThings, type_safety=TypeSafety.RELAXED) as my_mock:
            when(my_mock.method_with_missing_arg_hint("could_be_anything", True)).then_return(None)

    def test_specify_return_of_non_hinted_return(self):
        with tmock(ClassWithMultipleUnHintedThings, type_safety=TypeSafety.RELAXED) as my_mock:
            when(my_mock.method_with_missing_return_type()).then_return("something")


class TestTypeSafetyNoResponseIsNone(TestCase):

    def test_specify_return_to_be_Nonewhen_missing(self):
        with tmock(ClassWithNoResponseType, type_safety=TypeSafety.NO_RETURN_IS_NONE_RETURN) as my_mock:
            when(my_mock.method_with_missing_return_type()).then_return(None)

    def test_specify_return_to_be_something_elsewhen_missing(self):
        with self.assertRaises(MockTypeSafetyError):
            with tmock(ClassWithNoResponseType, type_safety=TypeSafety.NO_RETURN_IS_NONE_RETURN) as my_mock:
                when(my_mock.method_with_missing_return_type()).then_return("Something")
