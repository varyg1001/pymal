__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from pymal import decorators
from pymal.account_objects import account_list, my_anime


__all__ = ["AccountAnimes"]


class AccountAnimes(account_list.AccountList):
    """
    A slow loading of an account anime list.

    :ivar watching: :class:`frozenset` of the watching animes.
    :ivar completed: :class:`frozenset` of the completed animes.
    :ivar on_hold: :class:`frozenset` of the "on hold" animes.
    :ivar dropped: :class:`frozenset` of the dropped animes.
    :ivar plan_to_watch: :class:`frozenset` of th "plan to watch" animes.
    """

    _KIND = "anime"
    _ENTRY = my_anime.MyAnime
    _STATUS_NAMES = my_anime.STATUS_NAMES

    @property
    @decorators.load
    def watching(self) -> frozenset:
        return self._status(1)

    @property
    @decorators.load
    def completed(self) -> frozenset:
        return self._status(2)

    @property
    @decorators.load
    def on_hold(self) -> frozenset:
        return self._status(3)

    @property
    @decorators.load
    def dropped(self) -> frozenset:
        return self._status(4)

    @property
    @decorators.load
    def plan_to_watch(self) -> frozenset:
        return self._status(6)
