__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import singleton_factory

from pymal.account_objects import my_entry
from pymal.account_objects.my_entry import _Field


__all__ = ["MyAnime"]

STATUS_NAMES = {
    1: "watching",
    2: "completed",
    3: "on_hold",
    4: "dropped",
    6: "plan_to_watch",
}


class MyAnime(my_entry.MyEntry, metaclass=singleton_factory.SingletonFactory):
    """
    Saves an account data about anime.

    :ivar in_list: boolean, whether the account has the anime in its list.
    :ivar my_status: int, 1=watching, 2=completed, 3=on hold, 4=dropped, 6=plan to watch.
    :ivar my_score: int, 0 (no score) to 10.
    :ivar my_start_date: string as yyyymmdd, ``00000000`` if unset.
    :ivar my_end_date: string as yyyymmdd, ``00000000`` if unset.
    :ivar my_priority: int, 0 (low) to 2 (high).
    :ivar my_is_rewatching: boolean.
    :ivar my_completed_episodes: int.
    :ivar my_times_rewatched: int.
    :ivar my_rewatch_value: int, 0 to 5.
    :ivar my_tags: frozenset.
    :ivar my_comments: string

    Changing a value only changes it here; call :meth:`update` to send it to MAL.
    """

    _KIND = "anime"
    _STATUS_NAMES = STATUS_NAMES
    _WEB_FIELDS = {
        "my_status": ("status", "status"),
        "my_score": ("score", "score"),
        "my_completed_episodes": ("num_watched_episodes", "num_watched_episodes"),
    }

    my_status = my_entry.status_field(STATUS_NAMES)
    my_score = _Field("score", 0, valid=my_entry.int_between(0, 10))
    my_start_date = my_entry.date_field("start_date")
    my_end_date = my_entry.date_field("finish_date")
    my_priority = _Field("priority", 0, valid=my_entry.int_between(0, 2))
    my_is_rewatching = _Field("is_rewatching", False, valid=lambda v: isinstance(v, bool))
    my_completed_episodes = _Field(
        "num_episodes_watched",
        0,
        update_key="num_watched_episodes",
        valid=my_entry.at_least_zero,
    )
    my_times_rewatched = _Field("num_times_rewatched", 0, valid=my_entry.at_least_zero)
    my_rewatch_value = _Field("rewatch_value", 0, valid=my_entry.int_between(0, 5))
    my_tags = my_entry.tags_field()
    my_comments = _Field("comments", "", valid=lambda v: isinstance(v, str))

    def __init__(self, mal_id, account):
        """
        :param mal_id: the anime, or its MAL id.
        :param account: Which account this is connected to.
        :type account: :class:`account.Account`
        """
        from pymal import anime

        obj = mal_id if isinstance(mal_id, anime.Anime) else anime.Anime(mal_id)
        super().__init__(obj, account)

    def increase(self) -> bool:
        """
        Increasing the watched episodes by one; plan to watch becomes watching.

        :return: False if everything was watched already.
        :rtype: bool
        """
        if self.my_completed_episodes >= self.obj.episodes:
            return False
        self.my_completed_episodes += 1
        if self.my_status in (0, 6):
            self.my_status = 1
        return True

    @property
    def is_completed(self) -> bool:
        """
        :return: True if the number of completed episode is equal to number of episode in anime.
        :rtype: bool
        """
        return self.my_completed_episodes == self.obj.episodes

    def set_completed(self) -> bool:
        """
        Setting the anime as completed.

        :return: True if succeed
        :rtype: bool
        """
        if self.obj.episodes == float("inf"):
            return False
        self.my_completed_episodes = self.obj.episodes
        self.my_is_rewatching = False
        self.my_status = 2
        return True
