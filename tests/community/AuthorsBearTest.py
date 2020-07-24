import unittest

from bears.community.AuthorsBear import AuthorsBear


class AuthorsBearTest(unittest.TestCase):

    def test_arguments(self):
        self.assertEqual(AuthorsBear.create_arguments(
            'test'), ('contributor',))
