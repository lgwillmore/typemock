from unittest import TestCase

from typemock import match, tmock, when
from typemock.api import MockTypeSafetyError


class MyThing:

    def return_a_str(self) -> str:
        pass

    def convert_int_to_str(self, number: int) -> str:
        pass

    def multiple_arg(self, prefix: str, number: int) -> str:
        pass

    def do_something_with_side_effects(self) -> None:
        pass


class TestMatcherAny(TestCase):

    def test_something_equal_to_any_thing(self):
        matcher = match.anything()

        self.assertEqual(1, matcher)


class TestMockObjectMatching(TestCase):

    def test_specify_any_matcher_arg__called_with_correct_type__return_single(self):
        expected = "a string"
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(match.anything())).then_return(expected)

        actual = my_thing_mock.convert_int_to_str(2)

        self.assertEqual(expected, actual)

    def test_specify_any_matcher_arg__called_with_correct_type__return_many(self):
        expected_many = ["a string"]
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(match.anything())).then_return_many(expected_many)

        for expected in expected_many:
            actual = my_thing_mock.convert_int_to_str(2)
            self.assertEqual(expected, actual)

    def test_specify_any_matcher_arg__called_with_correct_type__raise_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(match.anything())).then_raise(IOError)

        with self.assertRaises(IOError):
            my_thing_mock.convert_int_to_str(2)

    def test_when_we_have_matcher_based_behaviour_type_safety_is_enforced_on_call(self):
        expected = "a string"
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(match.anything())).then_return(expected)

        with self.assertRaises(MockTypeSafetyError):
            my_thing_mock.convert_int_to_str("not an int")
