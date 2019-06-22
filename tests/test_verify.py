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

    def test_verify__at_least__no_calls__verify_error(self):
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

    def test_verify__at_least__other_calls__verify_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.some_instance_attribute).then_return("Hello")
            when(my_thing_mock.convert_int_to_str(match.anything())).then_return("bye")

        my_thing_mock.convert_int_to_str(1)

        # Method
        with self.assertRaises(VerifyError):
            verify(my_thing_mock).convert_int_to_str(2)

        my_thing_mock.some_instance_attribute = "something_else"

        # Set attribute
        with self.assertRaises(VerifyError):
            verify(my_thing_mock).some_instance_attribute = "hello2"

    def test_verify__at_least__was_called(self):
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

    def test_verify__exactly__not_matched__no_other_calls__verify_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.some_instance_attribute).then_return("Hello")
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)

        # Method
        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=1).do_something_with_side_effects()

        # Get attribute
        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=1).some_instance_attribute

        # Set attribute
        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=1).some_instance_attribute = "bye"

    def test_verify__exactly__not_matched__other_calls__verify_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.some_instance_attribute).then_return("Hello")
            when(my_thing_mock.convert_int_to_str(match.anything())).then_return("A string")

        my_thing_mock.convert_int_to_str(1)

        # Method
        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=2).convert_int_to_str(2)

        my_thing_mock.some_instance_attribute = "something else"

        # Set attribute
        with self.assertRaises(VerifyError):
            verify(my_thing_mock, exactly=2).some_instance_attribute = "bye"

    def test_verify__exactly__incorrect_amount_of_times__verify_error(self):
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
