__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"


from pymal import exceptions, global_functions
from pymal.decorators import load
from pymal.types import ReloadedSet


class AccountFriends(ReloadedSet.ReloadedSetSingletonFactory):
    """
    A slow load of friend list.

    :ivar account: the account to load his friends.
    """

    def __init__(self, account):
        """
        :param account: the account to get the friends.
        :type account: :class:`account.Account`
        """
        self.account = account
        self.__url = account._main_profile_url + "/friends"

        self.__friends = frozenset()

        self._is_loaded = False

    @property
    @load
    def __friends_list(self):
        return self.__friends

    @property
    def _values(self):
        return self.__friends_list

    def reload(self):
        """
        :exception FailedToParseError
        """
        div_wrapper = global_functions.get_content_wrapper_div(
            self.__url, self.account.connect
        )
        if div_wrapper is None:
            raise exceptions.FailedToParseError()

        # An empty or private friend list simply has no entries.
        list_div_friend = div_wrapper.select("div.boxlist-container.friend div.boxlist")
        self.__friends = frozenset(map(self.__parse_friend_div, list_div_friend))

        self._is_loaded = True

    @staticmethod
    def __parse_friend_div(div_friend):
        """
        :param div_friend: the ``div.boxlist`` of one friend.
        :exception FailedToParseError
        :return: the friend's account
        :rtype: :class:`account.Account`
        """
        from pymal import account

        link = div_friend.select_one("div.title a") or div_friend.find("a", href=True)
        if link is None:
            raise exceptions.FailedToParseError(div_friend)

        splited_friend_url = link["href"].split("/profile/", 1)
        if len(splited_friend_url) != 2:
            raise exceptions.FailedToParseError(link["href"])

        return account.Account(splited_friend_url[1])

    def __repr__(self):
        return f"<User friends' number is {len(self):d}>"

    def __hash__(self):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(self.account.username.encode())
        hash_md5.update(self.__class__.__name__.encode())
        return int(hash_md5.hexdigest(), 16)
