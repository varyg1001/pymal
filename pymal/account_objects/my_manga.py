__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import singleton_factory

from pymal.account_objects import my_entry
from pymal.account_objects.my_entry import _Field


__all__ = ["MyManga"]

STATUS_NAMES = {
    1: "reading",
    2: "completed",
    3: "on_hold",
    4: "dropped",
    6: "plan_to_read",
}


class MyManga(my_entry.MyEntry, metaclass=singleton_factory.SingletonFactory):
    """
    Saves an account data about manga.

    :ivar in_list: boolean, whether the account has the manga in its list.
    :ivar my_status: int, 1=reading, 2=completed, 3=on hold, 4=dropped, 6=plan to read.
    :ivar my_score: int, 0 (no score) to 10.
    :ivar my_start_date: string as yyyymmdd, ``00000000`` if unset.
    :ivar my_end_date: string as yyyymmdd, ``00000000`` if unset.
    :ivar my_priority: int, 0 (low) to 2 (high).
    :ivar my_is_rereading: boolean.
    :ivar my_completed_chapters: int.
    :ivar my_completed_volumes: int.
    :ivar my_times_reread: int.
    :ivar my_reread_value: int, 0 to 5.
    :ivar my_tags: frozenset.
    :ivar my_comments: string

    Changing a value only changes it here; call :meth:`update` to send it to MAL.
    """

    _KIND = "manga"
    _STATUS_NAMES = STATUS_NAMES
    _WEB_FIELDS = {
        "my_status": ("status", "status"),
        "my_score": ("score", "score"),
        "my_completed_chapters": ("num_read_chapters", "num_read_chapters"),
        "my_completed_volumes": ("num_read_volumes", "num_read_volumes"),
    }

    my_status = my_entry.status_field(STATUS_NAMES)
    my_score = _Field("score", 0, valid=my_entry.int_between(0, 10))
    my_start_date = my_entry.date_field("start_date")
    my_end_date = my_entry.date_field("finish_date")
    my_priority = _Field("priority", 0, valid=my_entry.int_between(0, 2))
    my_is_rereading = _Field("is_rereading", False, valid=lambda v: isinstance(v, bool))
    my_completed_chapters = _Field("num_chapters_read", 0, valid=my_entry.at_least_zero)
    my_completed_volumes = _Field("num_volumes_read", 0, valid=my_entry.at_least_zero)
    my_times_reread = _Field("num_times_reread", 0, valid=my_entry.at_least_zero)
    my_reread_value = _Field("reread_value", 0, valid=my_entry.int_between(0, 5))
    my_tags = my_entry.tags_field()
    my_comments = _Field("comments", "", valid=lambda v: isinstance(v, str))

    def __init__(self, mal_id, account):
        """
        :param mal_id: the manga, or its MAL id.
        :param account: Which account this is connected to.
        :type account: :class:`account.Account`
        """
        from pymal import manga

        obj = mal_id if isinstance(mal_id, manga.Manga) else manga.Manga(mal_id)
        super().__init__(obj, account)

    def increase(self) -> bool:
        """
        Increasing the read chapters by one; plan to read becomes reading.

        :return: False if everything was read already.
        :rtype: bool
        """
        if self.my_completed_chapters >= self.obj.chapters:
            return False
        self.my_completed_chapters += 1
        if self.my_status in (0, 6):
            self.my_status = 1
        return True

    def increase_volume(self) -> bool:
        """
        Increasing the read volumes by one.

        :return: False if all the volumes were read already.
        :rtype: bool
        """
        if self.my_completed_volumes >= self.obj.volumes:
            return False
        self.my_completed_volumes += 1
        return True

    @property
    def is_completed(self) -> bool:
        """
        :return: True if the number of completed chapters is equal to number of chapters in manga.
        :rtype: bool
        """
        return self.my_completed_chapters >= self.obj.chapters

    def set_completed(self) -> bool:
        """
        Setting the manga as completed.

        :return: True if succeed
        :rtype: bool
        """
        if self.obj.chapters == float("inf"):
            return False
        self.my_completed_chapters = self.obj.chapters
        if self.obj.volumes != float("inf"):
            self.my_completed_volumes = self.obj.volumes
        self.my_is_rereading = False
        self.my_status = 2
        return True
