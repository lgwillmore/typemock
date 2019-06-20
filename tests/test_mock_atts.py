from typing import List
from unittest import TestCase

from typemock import tmock, when


class MyThing:
    _private_att = None  # <- dont care
    class_att_with_type: int = 1  # <- typed, easy
    class_att_with_typed_init = "bar"  # <- type determined from __init__ annotation.
    generic_att: List[str] = []

    def __init__(
            self,
            class_att_with_typed_init: str,  # <- provides type for class level attribute
            instance_att_typed_init: int,  # <- provides type for instance attribute
    ):
        self.class_att_with_typed_init = class_att_with_typed_init
        self.instance_att_typed_init = instance_att_typed_init  # <- type from init

    @property
    def derived_property_throws_error(self) -> str:
        if self.instance_att_typed_init is None:
            raise Exception("Cannot derive")
        return "hello"

    @property
    def derived_property(self) -> str:
        return "bye"


mocked_things = [
    MyThing,
    MyThing(
        class_att_with_typed_init="init_1",
        instance_att_typed_init=99,
    )
]


class TestBasicClassAttributeMocking(TestCase):

    def test_mock__class_attribute__get__simple_return(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected = 3

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.class_att_with_type).then_return(expected)

                actual = my_thing_mock.class_att_with_type

                self.assertEqual(expected, actual)

    def test_mock__generic_attribute__get__simple_return(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected = ["hello"]

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.generic_att).then_return(expected)

                actual = my_thing_mock.generic_att

                self.assertEqual(expected, actual)

    def test_mock__class_attribute__get__many(self):
        expected_responses = [
            3,
            4
        ]

        for mocked_thing in mocked_things:
            with self.subTest():

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.class_att_with_type).then_return_many(expected_responses)

                for expected in expected_responses:
                    actual = my_thing_mock.class_att_with_type
                    self.assertEqual(expected, actual)

    def test_mock__class_attribute__get__then_raise(self):
        expected_error = IOError()

        for mocked_thing in mocked_things:
            with self.subTest():
                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.class_att_with_type).then_raise(expected_error)

                with self.assertRaises(IOError):
                    my_thing_mock.class_att_with_type

    def test_mock__class_attribute__get__then_do(self):
        expected = 3

        def handle_get():
            return expected

        for mocked_thing in mocked_things:
            with self.subTest():
                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.class_att_with_type).then_do(handle_get)

                actual = my_thing_mock.class_att_with_type

                self.assertEqual(expected, actual)

    def test_mock__class_attribute__get__no_behaviour(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                my_thing_mock = tmock(mocked_thing)

                result = my_thing_mock.class_att_with_type

                self.assertEqual(mocked_thing.class_att_with_type, result)

    def test_mock__class_attribute__set_then_get(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                mocked_with = 1

                with tmock(MyThing) as my_thing_mock:
                    when(my_thing_mock.instance_att_typed_init).then_return(mocked_with)

                setting_to = 3

                my_thing_mock.class_att_with_type = setting_to

                self.assertEqual(mocked_thing.class_att_with_type, mocked_with)

    def test_mock__instance_attribute__get__simple_return(self):
        expected = 2

        for mocked_thing in mocked_things:
            with self.subTest():
                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.instance_att_typed_init).then_return(expected)

                actual = my_thing_mock.instance_att_typed_init

                self.assertEqual(expected, actual)

    def test_mock__property__get__simple_return(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected = "hello"

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.derived_property).then_return(expected)

                actual = my_thing_mock.derived_property

                self.assertEqual(expected, actual)

    def test_mock__property_with_error__get__simple_return(self):
        for mocked_thing in mocked_things:
            with self.subTest():
                expected = "hello"

                with tmock(mocked_thing) as my_thing_mock:
                    when(my_thing_mock.derived_property_throws_error).then_return(expected)

                actual = my_thing_mock.derived_property_throws_error

                self.assertEqual(expected, actual)
