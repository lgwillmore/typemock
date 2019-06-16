from unittest import TestCase

from typemock import tmock, when, verify
from typemock.api import NoBehaviourSpecifiedError


class MyThing:
    def return_a_str(self) -> str:
        pass

    def convert_int_to_str(self, number: int) -> str:
        pass

    def multiple_arg(self, prefix: str, number: int) -> str:
        pass

    def do_something_with_side_effects(self) -> None:
        pass

    def method_with_default_args(self, first_number: int, second_string: str = "default") -> None:
        pass


mocked_things = [MyThing, MyThing()]


class TestBasicMethodMocking(TestCase):

    def test_mock__isinstance_of_mocked_class(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                my_thing_mock = tmock(mocked_thing)

                self.assertIsInstance(my_thing_mock, MyThing)

    def test_mock__can_mock_method__no_args__returns(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected_result = "a string"

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.return_a_str()).then_return(expected_result)

                actual = my_thing_mock.return_a_str()

                self.assertEqual(expected_result, actual)
                verify(my_thing_mock).return_a_str()

    def test_mock__unmocked_method__NoBehaviourError(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                my_thing_mock: MyThing = tmock(mocked_thing)

                with self.assertRaises(NoBehaviourSpecifiedError):
                    my_thing_mock.return_a_str()

    def test_mock__try_to_mock_method_out_of_context(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                my_thing_mock: MyThing = tmock(mocked_thing)

                with self.assertRaises(NoBehaviourSpecifiedError):
                    when(my_thing_mock.return_a_str()).then_return("some string")

    def test_mock__can_mock_method__arg__returns(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected_result = "a string"

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.convert_int_to_str(1)).then_return(expected_result)

                actual = my_thing_mock.convert_int_to_str(1)

                self.assertEqual(expected_result, actual)
                verify(my_thing_mock).convert_int_to_str(1)

    def test_mock__can_mock_method__multiple_args__returns(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected_result = "a string"

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.multiple_arg("p", 1)).then_return(expected_result)

                actual = my_thing_mock.multiple_arg("p", 1)

                self.assertEqual(expected_result, actual)
                verify(my_thing_mock).multiple_arg("p", 1)

    def test_mock__can_mock_method__multiple_args__mixed_with_kwargs_in_usage(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected_result = "a string"

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.multiple_arg("p", 1)).then_return(expected_result)

                actual = my_thing_mock.multiple_arg(
                    number=1,
                    prefix="p"
                )

                self.assertEqual(expected_result, actual)
                verify(my_thing_mock).multiple_arg("p", 1)

    def test_mock__can_mock_method__multiple_args__mixed_with_kwargs_in_setup(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected_result = "a string"

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.multiple_arg(number=1, prefix="p")).then_return(expected_result)

                actual = my_thing_mock.multiple_arg("p", 1)

                self.assertEqual(expected_result, actual)
                verify(my_thing_mock).multiple_arg("p", 1)

    def test_mock__can_mock_method__default_args(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.method_with_default_args(first_number=1)).then_return(None)

                my_thing_mock.method_with_default_args(1)

                verify(my_thing_mock).method_with_default_args(1)

    def test_mock__can_mock_method__no_args__no_return(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.do_something_with_side_effects()).then_return(None)

                my_thing_mock.do_something_with_side_effects()

                verify(my_thing_mock).do_something_with_side_effects()

    def test_mock__then_raise(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected_error = IOError()

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.do_something_with_side_effects()).then_raise(expected_error)

                with self.assertRaises(IOError):
                    my_thing_mock.do_something_with_side_effects()

    def test_mock__then_return_many__loop_false(self):
        expected_responses = [
            "first response",
            "second response"
        ]

        for mocked_thing in mocked_things:
            with self.subTest():

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.return_a_str()).then_return_many(expected_responses, False)

                for expected in expected_responses:
                    actual = my_thing_mock.return_a_str()
                    self.assertEqual(expected, actual)

                # Not looping, and responses have run out.
                with self.assertRaises(NoBehaviourSpecifiedError):
                    my_thing_mock.return_a_str()

    def test_mock__then_return_many__loop_true(self):
        expected_responses = [
            "first response",
            "second response"
        ]

        for mocked_thing in mocked_things:
            with self.subTest():
                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.return_a_str()).then_return_many(expected_responses, True)

                for i in range(2):
                    for expected in expected_responses:
                        actual = my_thing_mock.return_a_str()
                        self.assertEqual(expected, actual)

# TODO: We can still mock a context object - idea: setup can only happen on_first - successive contexts revert.
