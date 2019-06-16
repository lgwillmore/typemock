from unittest import TestCase

from typemock import tmock


class MyThingEmptyInit:
    pass


class MyThingInitWithArgs:

    def __init__(self, an_attribute: int):
        self.an_attribute = an_attribute


class MyThingInitWithArgsAndLogic:

    def __init__(self, an_attribute: int):
        self.an_attribute = an_attribute + 3


class TestMockClass(TestCase):

    def test_mock__class__empty_init__no_errors(self):
        tmock(MyThingEmptyInit)

    def test_mock__class__init_with_args__no_errors(self):
        tmock(MyThingInitWithArgs)

    def test_mock__class__init_with_args_and_complex_logic__no_errors(self):
        tmock(MyThingInitWithArgsAndLogic)
