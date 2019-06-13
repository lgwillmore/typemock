from unittest import TestCase

from typemock import tmock, when, verify, match
from typemock.api import VerifyError


class MyThing:
    some_instance_attribute: str = None

    def return_a_str(self) -> str:
        pass

    def convert_int_to_str(self, number: int) -> str:
        pass

    def multiple_arg(self, prefix: str, number: int) -> str:
        pass

    def do_something_with_side_effects(self) -> None:
        pass


class TestMockVerify(TestCase):

    def test_verify__not_called__verify_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.some_instance_attribute).then_return("Hello")
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)

        with self.assertRaises(VerifyError):
            verify(my_thing_mock).do_something_with_side_effects()

        with self.assertRaises(VerifyError):
            verify(my_thing_mock).some_instance_attribute

    def test_verify__called(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.some_instance_attribute).then_return("Hello")
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)

        my_thing_mock.do_something_with_side_effects()
        my_thing_mock.some_instance_attribute

        verify(my_thing_mock).do_something_with_side_effects()
        verify(my_thing_mock).some_instance_attribute

    def test_verify__not_called__verify_exact_calls_0(self):
        my_thing_mock = tmock(MyThing)

        verify(my_thing_mock, exactly=0).do_something_with_side_effects()
        verify(my_thing_mock, exactly=0).some_instance_attribute

    def test_verify_called__incorrect_amount_of_times__verify_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)
            when(my_thing_mock.some_instance_attribute).then_return("hello")

        my_thing_mock.do_something_with_side_effects()
        my_thing_mock.some_instance_attribute

        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=2).do_something_with_side_effects()

        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=2).some_instance_attribute

    def test_verify__any_matcher__method_called(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(1)).then_return("something")

        my_thing_mock.convert_int_to_str(1)

        verify(my_thing_mock).convert_int_to_str(match.anything())

    def test_verify__any_matcher__method_not_called(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(1)).then_return("something")

        with self.assertRaises(VerifyError):
            verify(my_thing_mock).convert_int_to_str(match.anything())
