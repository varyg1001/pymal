__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

from urllib import request

from pymal import decorators, global_functions
from pymal.consts import HOST_NAME
from pymal.types import ReloadedSet


__all__ = ["AccountAnimes"]


class AccountAnimes(ReloadedSet.ReloadedSetSingletonFactory):
    """
    A slow loading of an account anime list.

    :ivar watching: :class:`frozenset` of the watching animes.
    :ivar completed: :class:`frozenset` of the completed animes.
    :ivar on_hold: :class:`frozenset` of the "on hold" animes.
    :ivar dropped: :class:`frozenset` of the dropped animes.
    :ivar plan_to_watch: :class:`frozenset` of th "plan to watch" animes.
    """

    __URL = request.urljoin(HOST_NAME, "animelist/{0:s}&status=")

    def __init__(self, account):
        """
        :param account: Which account this anime list is connected to.
        :type account: :class:`account.Account`
        """
        self.__account = account
        self.__url = self.__URL.format(account.username)

        self._watching = frozenset()
        self._completed = frozenset()
        self._on_hold = frozenset()
        self._dropped = frozenset()
        self._plan_to_watch = frozenset()

        self.map_of_lists = {
            1: self._watching,
            2: self._completed,
            3: self._on_hold,
            4: self._dropped,
            6: self._plan_to_watch,
            "1": self._watching,
            "2": self._completed,
            "3": self._on_hold,
            "4": self._dropped,
            "6": self._plan_to_watch,
            "watching": self._watching,
            "completed": self._completed,
            "onhold": self._on_hold,
            "dropped": self._dropped,
            "plantowatch": self._plan_to_watch,
        }

        self._is_loaded = False

    @property
    @decorators.load
    def watching(self) -> frozenset:
        """
        :return: The watching list
        :rtype: frozenset
        """
        return self._watching

    @property
    @decorators.load
    def completed(self) -> frozenset:
        """
        :return: The completed list
        :rtype: frozenset
        """
        return self._completed

    @property
    @decorators.load
    def on_hold(self) -> frozenset:
        """
        :return: The on hold list
        :rtype: frozenset
        """
        return self._on_hold

    @property
    @decorators.load
    def dropped(self) -> frozenset:
        """
        :return: The dropped list
        :rtype: frozenset
        """
        return self._dropped

    @property
    @decorators.load
    def plan_to_watch(self) -> frozenset:
        """
        :return: The plan to watch list
        :rtype: frozenset
        """
        return self._plan_to_watch

    @property
    def _values(self) -> frozenset:
        """
        :return: The all the animes
        :rtype: frozenset
        """
        return (
            self.watching
            | self.completed
            | self.on_hold
            | self.dropped
            | self.plan_to_watch
        )

    def reload(self):
        """
        reloading data from MAL.
        """
        self._watching = self.__get_my_animes(1)
        self._completed = self.__get_my_animes(2)
        self._on_hold = self.__get_my_animes(3)
        self._dropped = self.__get_my_animes(4)
        self._plan_to_watch = self.__get_my_animes(6)

        self.map_of_lists[1] = self._watching
        self.map_of_lists[2] = self._completed
        self.map_of_lists[3] = self._on_hold
        self.map_of_lists[4] = self._dropped
        self.map_of_lists[6] = self._plan_to_watch
        self.map_of_lists["1"] = self._watching
        self.map_of_lists["2"] = self._completed
        self.map_of_lists["3"] = self._on_hold
        self.map_of_lists["4"] = self._dropped
        self.map_of_lists["6"] = self._plan_to_watch
        self.map_of_lists["watching"] = self._watching
        self.map_of_lists["completed"] = self._completed
        self.map_of_lists["onhold"] = self._on_hold
        self.map_of_lists["dropped"] = self._dropped
        self.map_of_lists["plantowatch"] = self._plan_to_watch

        self._is_loaded = True

    def __get_my_animes(self, status: int) -> frozenset:
        from pymal.account_objects.my_anime import MyAnime as obj

        url = f"{HOST_NAME}/animelist/{self.__account.username}/load.json?status={status}&offset=0"
        if self.__account.is_auth:
            sock = self.__account.auth_connect(url)
            import json

            data = json.loads(sock)
        else:
            sock = global_functions._connect(url)
            if sock.status_code != 200:
                return frozenset()
            data = sock.json()

        animes = set()
        for item in data:
            anime_id = item.get("anime_id")
            if anime_id:
                animes.add(obj(int(anime_id), 0, self.__account))
        return frozenset(animes)

    def __repr__(self):
        return f"<User animes' number is {len(self):d}>"

    def __hash__(self):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(self.__account.username.encode())
        hash_md5.update(self.__class__.__name__.encode())
        return int(hash_md5.hexdigest(), 16)
