from unittest import TestCase

from typemock import tmock, when


class MyThing:
    class_att_with_type: int = 1  # <- typed, easy
    class_att_with_typed_init = "bar"  # <- type determined from __init__ annotation.

    def __init__(
            self,
            class_att_with_typed_init: str,  # <- provides type for class level attribute
            instance_att_typed_init: int,  # <- provides type for instance attribute
    ):
        self.class_att_with_typed_init = class_att_with_typed_init
        self.instance_att_typed_init = instance_att_typed_init  # <- type from init


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

    def test_mock__class_attribute__get__multiple(self):
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
