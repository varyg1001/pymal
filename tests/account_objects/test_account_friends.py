import unittest

from pymal import account
from tests.constants_for_testing import make_account


class InitTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = make_account()

    def test_friends(self):
        for friend in self.account.friends:
            self.assertIsInstance(friend, account.Account)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
