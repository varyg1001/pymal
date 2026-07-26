__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

from singleton3 import Singleton

from pymal import decorators


__all__ = ["Seasons"]


class Seasons(metaclass=Singleton):
    """
    Lazy making of Season from online db.

    :ivar seasons: :class:`frozenset` of :class:`inner_objects..season.Season`.
    """

    __SEASONS_URL = "{0:s}/anime/season/archive"

    def __init__(self):
        self.__seasons = frozenset()
        self._is_loaded = False

    @property
    @decorators.load
    def seasons(self) -> frozenset:
        return self.__seasons

    def reload(self):
        """
        reloading all the known seasons.
        """
        import re

        import bs4

        from pymal import consts, global_functions
        from pymal.inner_objects import season

        url = self.__SEASONS_URL.format(consts.HOST_NAME)
        data = global_functions.connect(url)
        html = bs4.BeautifulSoup(data, "lxml")

        season_objs = set()
        for a in html.find_all("a"):
            href = a.get("href", "")
            match = re.search(
                r"/anime/season/(\d{4})/(winter|spring|summer|fall)", href, re.IGNORECASE
            )
            if match:
                year = int(match.group(1))
                season_name = match.group(2).capitalize()
                season_objs.add(season.Season(season_name, year))

        self.__seasons = frozenset(season_objs)
        self._is_loaded = True

    def __contains__(self, item) -> bool:
        return any(item in season for season in self.seasons)

    def __repr__(self):
        import os

        return (os.linesep + "\t").join(map(str, ["<Seasons>"] + list(self.seasons)))

    def __iter__(self):
        return iter(self.seasons)

    def __len__(self) -> int:
        return sum(len(x) for x in self.seasons)
