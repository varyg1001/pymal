import unittest

from pymal import account, manga
from pymal.account_objects import account_mangas
from tests.constants_for_testing import (
    ACCOUNT_TEST_PASSWORD,
    ACCOUNT_TEST_USERNAME,
    MANGA_ID,
)


class AccountMangaListTestCase(unittest.TestCase):
    EXPECTED_LENGTH = 1

    @classmethod
    def setUpClass(cls):
        cls.account = account.Account(ACCOUNT_TEST_USERNAME, ACCOUNT_TEST_PASSWORD)
        cls.mangas = cls.account.mangas

    @classmethod
    def tearDownClass(cls):
        account_mangas.AccountMangas._unregiter(cls.mangas)
        account.Account._unregiter(cls.account)

    def test_len(self):
        self.assertEqual(len(self.mangas), self.EXPECTED_LENGTH)

    def test_contains_manga(self):
        my_manga = list(self.mangas)[0]
        mng = manga.Manga(my_manga.id)
        self.assertIn(mng, self.mangas)

    def test_contains_my_manga(self):
        my_manga = list(self.mangas)[0]
        self.assertIn(my_manga, self.mangas)

    def test_contains_id(self):
        self.assertIn(MANGA_ID, self.mangas)

    def test_str(self):
        self.assertEqual(
            str(self.mangas), f"<User mangas' number is {self.EXPECTED_LENGTH:d}>"
        )


class AccountMangaListInteraction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = account.Account(ACCOUNT_TEST_USERNAME, ACCOUNT_TEST_PASSWORD)
        cls.friend = list(cls.account.friends)[0]
        cls.mangas = cls.account.mangas
        cls.friend_mangas = cls.friend.mangas

    @classmethod
    def tearDownClass(cls):
        account_mangas.AccountMangas._unregiter(cls.friend_mangas)
        account_mangas.AccountMangas._unregiter(cls.mangas)
        account.Account._unregiter(cls.friend)
        account.Account._unregiter(cls.account)

    def test_union(self):
        regular = self.mangas.union(self.friend_mangas)
        operator = self.mangas | self.friend_mangas
        self.assertEqual(regular, operator)

    def test_intersection(self):
        regular = self.mangas.intersection(self.friend_mangas)
        operator = self.mangas & self.friend_mangas
        self.assertEqual(regular, operator)

    def test_difference(self):
        regular = self.mangas.difference(self.friend_mangas)
        operator = self.mangas - self.friend_mangas
        self.assertEqual(regular, operator)

    def test_symmetric_difference(self):
        regular = self.mangas.symmetric_difference(self.friend_mangas)
        operator = self.mangas ^ self.friend_mangas
        self.assertEqual(regular, operator)

    def test_issubset(self):
        regular = self.mangas.issubset(self.friend_mangas)
        operator = self.mangas <= self.friend_mangas
        self.assertEqual(regular, operator)

    def test_issuperset(self):
        regular = self.mangas.issubset(self.friend_mangas)
        operator = self.mangas >= self.friend_mangas
        self.assertEqual(regular, operator)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
