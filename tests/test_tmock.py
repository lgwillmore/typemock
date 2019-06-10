from unittest import TestCase

from typemock import tmock, when, verify
from typemock._verify import VerifyError
from typemock.api import NoBehaviourSpecifiedError, MockTypeSafetyError


class MyThing:

    def return_a_str(self) -> str:
        pass

    def convert_int_to_str(self, number: int) -> str:
        pass

    def multiple_arg(self, prefix: str, number: int) -> str:
        pass

    def do_something_with_side_effects(self) -> None:
        pass


class TestBasicMethodMocking(TestCase):

    def test_mock_object__isinstance_of_mocked_class(self):
        my_thing_mock = tmock(MyThing)

        self.assertIsInstance(my_thing_mock, MyThing)

    def test_mock_object__can_mock_method__no_args__returns(self):
        expected_result = "a string"

        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.return_a_str()).then_return(expected_result)

        actual = my_thing_mock.return_a_str()

        self.assertEqual(expected_result, actual)
        verify(my_thing_mock).return_a_str()

    def test_mock_object__unmocked_method__NoBehaviourError(self):
        my_thing_mock: MyThing = tmock(MyThing)

        with self.assertRaises(NoBehaviourSpecifiedError):
            my_thing_mock.return_a_str()

    def test_mock_object__try_to_mock_method_out_of_context(self):
        my_thing_mock: MyThing = tmock(MyThing)

        with self.assertRaises(NoBehaviourSpecifiedError):
            when(my_thing_mock.return_a_str()).then_return("some string")

    def test_mock_object__can_mock_method__arg__returns(self):
        expected_result = "a string"

        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.convert_int_to_str(1)).then_return(expected_result)

        actual = my_thing_mock.convert_int_to_str(1)

        self.assertEqual(expected_result, actual)
        verify(my_thing_mock).convert_int_to_str(1)

    def test_mock_object__can_mock_method__multiple_args__returns(self):
        expected_result = "a string"

        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.multiple_arg("p", 1)).then_return(expected_result)

        actual = my_thing_mock.multiple_arg("p", 1)

        self.assertEqual(expected_result, actual)
        verify(my_thing_mock).multiple_arg("p", 1)

    def test_mock_object__can_mock_method__multiple_args__mixed_with_kwargs_in_usage(self):
        expected_result = "a string"

        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.multiple_arg("p", 1)).then_return(expected_result)

        actual = my_thing_mock.multiple_arg(
            number=1,
            prefix="p"
        )

        self.assertEqual(expected_result, actual)
        verify(my_thing_mock).multiple_arg("p", 1)

    def test_mock_object__can_mock_method__multiple_args__mixed_with_kwargs_in_setup(self):
        expected_result = "a string"

        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.multiple_arg(number=1, prefix="p")).then_return(expected_result)

        actual = my_thing_mock.multiple_arg("p", 1)

        self.assertEqual(expected_result, actual)
        verify(my_thing_mock).multiple_arg("p", 1)

    def test_mock_object__can_mock_method__no_args__no_return(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)

        my_thing_mock.do_something_with_side_effects()

        verify(my_thing_mock).do_something_with_side_effects()

    def test_mock_object__mocked_method_not_called__verify_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)

        with self.assertRaises(VerifyError):
            verify(my_thing_mock).do_something_with_side_effects()

    # TODO: We can still mock a context object - idea: setup can only happen on_first - successive contexts revert.




