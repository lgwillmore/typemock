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

        # Method
        with self.assertRaises(VerifyError):
            verify(my_thing_mock).do_something_with_side_effects()

        # Get attribute
        with self.assertRaises(VerifyError):
            verify(my_thing_mock).some_instance_attribute

        # Set attribute
        with self.assertRaises(VerifyError):
            verify(my_thing_mock).some_instance_attribute = "bye"

    def test_verify__called(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.some_instance_attribute).then_return("Hello")
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)

        # Method
        my_thing_mock.do_something_with_side_effects()

        verify(my_thing_mock).do_something_with_side_effects()

        # Get Attribute
        my_thing_mock.some_instance_attribute

        verify(my_thing_mock).some_instance_attribute

        # Set Attribute
        my_thing_mock.some_instance_attribute = "bye"

        verify(my_thing_mock).some_instance_attribute = "bye"

    def test_verify__not_called__verify_exact_calls_0(self):
        my_thing_mock = tmock(MyThing)

        # Method
        verify(my_thing_mock, exactly=0).do_something_with_side_effects()

        # Get Attribute
        verify(my_thing_mock, exactly=0).some_instance_attribute

        # Set Attribute
        verify(my_thing_mock, exactly=0).some_instance_attribute = "one"

    def test_verify_called__incorrect_amount_of_times__verify_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)
            when(my_thing_mock.some_instance_attribute).then_return("hello")

        # Method
        my_thing_mock.do_something_with_side_effects()

        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=2).do_something_with_side_effects()

        # Get Attribute
        my_thing_mock.some_instance_attribute

        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=2).some_instance_attribute

        # Set Attribute
        my_thing_mock.some_instance_attribute = "bye"

        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=2).some_instance_attribute = "bye"

    def test_verify__any_matcher(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(1)).then_return("something")
            when(my_thing_mock.some_instance_attribute).then_return("hello")

        # Method
        my_thing_mock.convert_int_to_str(1)

        verify(my_thing_mock).convert_int_to_str(match.anything())

        # Set Attribute
        my_thing_mock.some_instance_attribute = "bye"

        verify(my_thing_mock).some_instance_attribute = match.anything()

    def test_verify__any_matcher__not_called(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(1)).then_return("something")
            when(my_thing_mock.some_instance_attribute).then_return("hello")

        with self.assertRaises(VerifyError):
            verify(my_thing_mock).convert_int_to_str(match.anything())

        with self.assertRaises(VerifyError):
            verify(my_thing_mock).some_instance_attribute = match.anything()
