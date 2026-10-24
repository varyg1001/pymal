__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from pymal import decorators, global_functions
from pymal.consts import HOST_NAME
from pymal.types import ReloadedSet


__all__ = ["AccountList"]


class AccountList(ReloadedSet.ReloadedSetSingletonFactory):
    """
    Base of :class:`account_animes.AccountAnimes` and :class:`account_mangas.AccountMangas`:
    a slow loading of an account list.

    With API credentials (see :meth:`account.Account.login`) the list comes from MAL's
    API, entries know their data and private lists work. With only a website session
    (:meth:`account.Account.login_with_cookie`) it comes from the website, with the
    status, score and progress of the entries. Without, only the public list is read
    from the website, as bare entries.
    """

    _KIND = ""  # "anime" or "manga"
    _ENTRY = None  # the class of the entries
    _STATUS_NAMES = {}  # {number: api status name}

    def __init__(self, account):
        """
        :param account: Which account this list is connected to.
        :type account: :class:`account.Account`
        """
        self._account = account
        self._lists = {number: frozenset() for number in self._STATUS_NAMES}
        self._is_loaded = False

    def _status(self, number: int) -> frozenset:
        return self._lists[number]

    @property
    @decorators.load
    def _values(self) -> frozenset:
        """
        :return: All the entries
        :rtype: frozenset
        """
        return frozenset().union(*self._lists.values())

    def reload(self):
        """
        reloading data from MAL.
        """
        entry_class = self._ENTRY
        numbers = {name: number for number, name in self._STATUS_NAMES.items()}
        lists = {number: set() for number in self._STATUS_NAMES}

        if self._account.has_api_access:
            path = f"/users/{self._account.username}/{self._KIND}list"
            fields = ",".join(field.key for field in entry_class._FIELDS)
            params = {"limit": 1000, "nsfw": 1, "fields": f"list_status{{{fields}}}"}
            for item in self._account.api_pages(path, params):
                number = numbers.get(item.get("list_status", {}).get("status"))
                if number is None:
                    continue
                entry = entry_class(item["node"]["id"], self._account)
                entry._load_status(item["list_status"])
                lists[number].add(entry)
        elif self._account.has_session:
            names = self._STATUS_NAMES
            for item in self._account.web.list_items(self._KIND, self._account.username):
                number = item.get("status")
                mal_id = item.get(f"{self._KIND}_id")
                if number in names and mal_id:
                    entry = entry_class(int(mal_id), self._account)
                    entry._load_status(entry._web_to_status(item))
                    lists[number].add(entry)
        else:
            for number in self._STATUS_NAMES:
                url = (
                    f"{HOST_NAME}/{self._KIND}list/{self._account.username}"
                    f"/load.json?status={number}"
                )
                for item in global_functions.fetch_public_list_json(url):
                    mal_id = item.get(f"{self._KIND}_id")
                    if mal_id:
                        lists[number].add(entry_class(int(mal_id), self._account))

        self._lists = {number: frozenset(entries) for number, entries in lists.items()}
        self._is_loaded = True

    def __repr__(self):
        return f"<User {self._KIND}s' number is {len(self):d}>"

    def __hash__(self):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(self._account.username.encode())
        hash_md5.update(self.__class__.__name__.encode())
        return int(hash_md5.hexdigest(), 16)
