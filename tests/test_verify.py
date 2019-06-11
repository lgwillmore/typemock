from unittest import TestCase

from typemock import tmock, when, verify
from typemock.api import VerifyError


class MyThing:

    def return_a_str(self) -> str:
        pass

    def convert_int_to_str(self, number: int) -> str:
        pass

    def multiple_arg(self, prefix: str, number: int) -> str:
        pass

    def do_something_with_side_effects(self) -> None:
        pass


class TestMockVerify(TestCase):

    def test_mock_object__mocked_method_not_called__verify_error(self):
        with tmock(MyThing) as my_thing_mock:
            when(my_thing_mock.do_something_with_side_effects()).then_return(None)

        with self.assertRaises(VerifyError):
            verify(my_thing_mock).do_something_with_side_effects()
