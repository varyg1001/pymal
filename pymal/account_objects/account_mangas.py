__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

from urllib import request

from pymal import decorators, global_functions
from pymal.consts import HOST_NAME
from pymal.types import ReloadedSet


__all__ = ["AccountMangas"]


class AccountMangas(ReloadedSet.ReloadedSetSingletonFactory):
    """
    A slow loading of an account anime list.

    :ivar reading: :class:`frozenset`
    :ivar completed: :class:`frozenset`
    :ivar on_hold: :class:`frozenset`
    :ivar dropped: :class:`frozenset`
    :ivar plan_to_read: :class:`frozenset`
    """

    __URL = request.urljoin(HOST_NAME, "mangalist/{0:s}&status=")

    def __init__(self, account):
        """
        :param account: Which account this manga list is connected to.
        :type account: :class:`account.Account`
        """
        self.__account = account
        self.__url = self.__URL.format(account.username)

        self._reading = frozenset()
        self._completed = frozenset()
        self._on_hold = frozenset()
        self._dropped = frozenset()
        self._plan_to_read = frozenset()

        self.map_of_lists = {
            1: self._reading,
            2: self._completed,
            3: self._on_hold,
            4: self._dropped,
            6: self._plan_to_read,
            "1": self._reading,
            "2": self._completed,
            "3": self._on_hold,
            "4": self._dropped,
            "6": self._plan_to_read,
            "reading": self._reading,
            "completed": self._completed,
            "onhold": self._on_hold,
            "dropped": self._dropped,
            "plantoread": self._plan_to_read,
        }

        self._is_loaded = False

    @property
    @decorators.load
    def reading(self) -> frozenset:
        return self._reading

    @property
    @decorators.load
    def completed(self) -> frozenset:
        return self._completed

    @property
    @decorators.load
    def on_hold(self) -> frozenset:
        return self._on_hold

    @property
    @decorators.load
    def dropped(self) -> frozenset:
        return self._dropped

    @property
    @decorators.load
    def plan_to_read(self) -> frozenset:
        return self._plan_to_read

    @property
    def _values(self) -> frozenset:
        return (
            self.reading
            | self.completed
            | self.on_hold
            | self.dropped
            | self.plan_to_read
        )

    def reload(self):
        """
        reloading data from MAL.
        """
        self._reading = self.__get_my_animes(1)
        self._completed = self.__get_my_animes(2)
        self._on_hold = self.__get_my_animes(3)
        self._dropped = self.__get_my_animes(4)
        self._plan_to_read = self.__get_my_animes(6)

        self.map_of_lists[1] = self._reading
        self.map_of_lists[2] = self._completed
        self.map_of_lists[3] = self._on_hold
        self.map_of_lists[4] = self._dropped
        self.map_of_lists[6] = self._plan_to_read
        self.map_of_lists["1"] = self._reading
        self.map_of_lists["2"] = self._completed
        self.map_of_lists["3"] = self._on_hold
        self.map_of_lists["4"] = self._dropped
        self.map_of_lists["6"] = self._plan_to_read
        self.map_of_lists["reading"] = self._reading
        self.map_of_lists["completed"] = self._completed
        self.map_of_lists["onhold"] = self._on_hold
        self.map_of_lists["dropped"] = self._dropped
        self.map_of_lists["plantoread"] = self._plan_to_read

        self._is_loaded = True

    def __get_my_animes(self, status: int) -> frozenset:
        from pymal.account_objects.my_manga import MyManga as obj

        url = f"{HOST_NAME}/mangalist/{self.__account.username}/load.json?status={status}&offset=0"
        try:
            if self.__account.is_auth:
                sock = self.__account.auth_connect(url)
                import json

                data = json.loads(sock)
            else:
                sock = global_functions._connect(url)
                if sock.status_code != 200:
                    return frozenset()
                data = sock.json()

            mangas = set()
            for item in data:
                manga_id = item.get("manga_id")
                if manga_id:
                    mangas.add(obj(int(manga_id), 0, self.__account))
            return frozenset(mangas)
        except Exception:
            return frozenset()

    def __repr__(self):
        return f"<User mangas' number is {len(self):d}>"

    def __hash__(self):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(self.__account.username.encode())
        hash_md5.update(self.__class__.__name__.encode())
        return int(hash_md5.hexdigest(), 16)
