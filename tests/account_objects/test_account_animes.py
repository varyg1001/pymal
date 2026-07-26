import unittest

from pymal import account, anime
from pymal.account_objects import account_animes, my_anime
from tests.constants_for_testing import (
    ACCOUNT_TEST_PASSWORD,
    ACCOUNT_TEST_USERNAME,
    ANIME_ID,
)


class AccountAnimeListTestCase(unittest.TestCase):
    EXPECTED_LENGTH = 1

    @classmethod
    def setUpClass(cls):
        cls.account = account.Account(ACCOUNT_TEST_USERNAME, ACCOUNT_TEST_PASSWORD)
        cls.animes = cls.account.animes

    @classmethod
    def tearDownClass(cls):
        account_animes.AccountAnimes._unregiter(cls.animes)
        account.Account._unregiter(cls.account)

    def test_len(self):
        self.assertEqual(len(self.animes), self.EXPECTED_LENGTH)

    def test_contains(self):
        anm = anime.Anime(ANIME_ID)
        self.assertIn(anm, self.animes)

    def test_contains_my_manga(self):
        my_anm = my_anime.MyAnime(ANIME_ID, 0, self.account)
        self.assertIn(my_anm, self.animes)

    def test_contains_id(self):
        self.assertIn(ANIME_ID, self.animes)

    def test_str(self):
        self.assertEqual(
            str(self.animes), f"<User animes' number is {self.EXPECTED_LENGTH:d}>"
        )


class AccountAnimeListInteraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = account.Account(ACCOUNT_TEST_USERNAME, ACCOUNT_TEST_PASSWORD)
        cls.friend = list(cls.account.friends)[0]
        cls.animes = cls.account.animes
        cls.friend_animes = cls.friend.animes

    @classmethod
    def tearDownClass(cls):
        account_animes.AccountAnimes._unregiter(cls.friend_animes)
        account_animes.AccountAnimes._unregiter(cls.animes)
        account.Account._unregiter(cls.friend)
        account.Account._unregiter(cls.account)

    def test_union(self):
        regular = self.animes.union(self.friend_animes)
        operator = self.animes | self.friend_animes
        self.assertEqual(regular, operator)

    def test_intersection(self):
        regular = self.animes.intersection(self.friend_animes)
        operator = self.animes & self.friend_animes
        self.assertEqual(regular, operator)

    def test_difference(self):
        regular = self.animes.difference(self.friend_animes)
        operator = self.animes - self.friend_animes
        self.assertEqual(regular, operator)

    def test_symmetric_difference(self):
        regular = self.animes.symmetric_difference(self.friend_animes)
        operator = self.animes ^ self.friend_animes
        self.assertEqual(regular, operator)

    def test_issubset(self):
        regular = self.animes.issubset(self.friend_animes)
        operator = self.animes <= self.friend_animes
        self.assertEqual(regular, operator)

    @unittest.skip("need to re think about this")
    def test_issuperset(self):
        regular = self.animes.issubset(self.friend_animes)
        operator = self.animes >= self.friend_animes
        self.assertEqual(regular, operator)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
