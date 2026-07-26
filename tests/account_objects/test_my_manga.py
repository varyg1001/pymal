import time
import unittest
from xml.etree import ElementTree

from pymal import account, consts, manga
from tests.constants_for_testing import ACCOUNT_TEST_PASSWORD, ACCOUNT_TEST_USERNAME


class ReloadTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = account.Account(ACCOUNT_TEST_USERNAME, ACCOUNT_TEST_PASSWORD)
        cls.manga = list(cls.account.mangas)[0]
        cls.manga.my_reload()

    def test_my_id(self):
        self.assertIsInstance(self.manga.my_id, int)

    def test_my_status(self):
        self.assertIsInstance(self.manga.my_status, int)

    def test_my_is_rereading(self):
        self.assertIsInstance(self.manga.my_is_rereading, bool)

    def test_my_completed_chapters(self):
        self.assertIsInstance(self.manga.my_completed_chapters, int)

    def test_my_completed_volumes(self):
        self.assertIsInstance(self.manga.my_completed_volumes, int)

    def test_my_tags(self):
        self.assertIsInstance(self.manga.my_tags, frozenset)

    def test_my_comments(self):
        self.assertIsInstance(self.manga.my_comments, str)

    def test_my_fan_sub_groups(self):
        self.assertIsInstance(self.manga.my_fan_sub_groups, str)

    def test_my_score(self):
        self.assertIsInstance(self.manga.my_start_date, str)

    def test_my_start_date(self):
        self.assertIsInstance(self.manga.my_start_date, str)
        try:
            self.assertEqual(self.manga.my_start_date, consts.MALAPI_NONE_TIME)
        except AssertionError:
            time.strptime(self.manga.my_start_date, consts.MALAPI_FORMAT_TIME)

    def test_my_end_date(self):
        self.assertIsInstance(self.manga.my_end_date, str)
        try:
            self.assertEqual(self.manga.my_end_date, consts.MALAPI_NONE_TIME)
        except AssertionError:
            time.strptime(self.manga.my_end_date, consts.MALAPI_FORMAT_TIME)

    def test_my_priority(self):
        self.assertIsInstance(self.manga.my_priority, int)

    def test_my_storage_type(self):
        self.assertIsInstance(self.manga.my_storage_type, int)

    def test_my_download_chapters(self):
        self.assertIsInstance(self.manga.my_downloaded_chapters, int)

    def test_my_times_reread(self):
        self.assertIsInstance(self.manga.my_times_reread, int)

    def test_my_reread_value(self):
        self.assertIsInstance(self.manga.my_reread_value, int)

    def test_to_xml(self):
        xml = self.manga.to_xml()
        ElementTree.fromstring(xml)

    def test_str(self):
        repr(self.manga)

    def test_update(self):
        self.manga.update()


class NoReloadTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = account.Account(ACCOUNT_TEST_USERNAME, ACCOUNT_TEST_PASSWORD)
        cls.manga = list(cls.account.mangas)[0]

    def test_my_id(self):
        self.assertIsInstance(self.manga.my_id, int)

    def test_my_status(self):
        self.assertIsInstance(self.manga.my_status, int)

    def test_my_is_rereading(self):
        self.assertIsInstance(self.manga.my_is_rereading, bool)

    def test_my_completed_chapters(self):
        self.assertIsInstance(self.manga.my_completed_chapters, int)

    def test_my_completed_volumes(self):
        self.assertIsInstance(self.manga.my_completed_volumes, int)

    def test_my_tags(self):
        self.assertIsInstance(self.manga.my_tags, frozenset)

    def test_my_start_date(self):
        self.assertIsInstance(self.manga.my_start_date, str)
        try:
            self.assertEqual(self.manga.my_start_date, consts.MALAPI_NONE_TIME)
        except AssertionError:
            time.strptime(self.manga.my_start_date, consts.MALAPI_FORMAT_TIME)

    def test_my_end_date(self):
        self.assertIsInstance(self.manga.my_end_date, str)
        try:
            self.assertEqual(self.manga.my_end_date, consts.MALAPI_NONE_TIME)
        except AssertionError:
            time.strptime(self.manga.my_end_date, consts.MALAPI_FORMAT_TIME)

    def test_my_times_reread(self):
        self.assertIsInstance(self.manga.my_times_reread, int)

    def test_my_reread_value(self):
        self.assertIsInstance(self.manga.my_reread_value, int)

    def test_equal(self):
        mng = manga.Manga(self.manga.id)
        self.assertEqual(mng, self.manga)

    def test_str(self):
        repr(self.manga)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
