from unittest import TestCase

from typemock._utils import InefficientUnHashableKeyDict


class TestInefficientHashableKeyDict(TestCase):

    def test__put__get(self):
        my_dict = InefficientUnHashableKeyDict()

        list_key1 = [1, 2]
        value1 = 1
        list_key2 = [1, 3]
        value2 = 2

        my_dict[list_key1] = value1
        my_dict[list_key2] = value2

        self.assertEqual(value1, my_dict[list_key1])
        self.assertEqual(value2, my_dict[list_key2])

        self.assertEqual(value1, my_dict.get(list_key1, None))
        self.assertEqual(None, my_dict.get(1, None))
