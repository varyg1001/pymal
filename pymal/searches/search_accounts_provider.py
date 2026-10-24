__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from pymal import account as account_module
from pymal.searches import search_provider


__all__ = ["SearchAccountsProvider"]


class SearchAccountsProvider(search_provider.SearchProvider):
    """
    Searching for accounts.
    """

    _SEARCH_NAME = "users"
    _PREFIX_TYPE = "user"
    _SEARCHED_URL_SUFFIX = "/profile/"

    @staticmethod
    def _prefix_key(item: dict) -> str | None:
        return item.get("name")

    def _SEARCHED_OBJECT(self, mal_url: str):

        return account_module.Account(mal_url)
