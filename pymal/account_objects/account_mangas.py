__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from pymal import decorators
from pymal.account_objects import account_list, my_manga


__all__ = ["AccountMangas"]


class AccountMangas(account_list.AccountList):
    """
    A slow loading of an account manga list.

    :ivar reading: :class:`frozenset` of the reading mangas.
    :ivar completed: :class:`frozenset` of the completed mangas.
    :ivar on_hold: :class:`frozenset` of the "on hold" mangas.
    :ivar dropped: :class:`frozenset` of the dropped mangas.
    :ivar plan_to_read: :class:`frozenset` of the "plan to read" mangas.
    """

    _KIND = "manga"
    _ENTRY = my_manga.MyManga
    _STATUS_NAMES = my_manga.STATUS_NAMES

    @property
    @decorators.load
    def reading(self) -> frozenset:
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
    def plan_to_read(self) -> frozenset:
        return self._status(6)
