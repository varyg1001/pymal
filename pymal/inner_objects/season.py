__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

import singleton_factory

from pymal import consts, decorators


__all__ = ["Season"]


class Season(metaclass=singleton_factory.SingletonFactory):
    """
    Lazy load of season data.

    Attributes:
        animes - a frozenset of animes.
        year - the season year.
        season_name - The season name. Can be 'Winter', 'Spring', 'Summer' or 'Fall'.
    """

    __all__ = ["animes", "reload"]

    __SEASON_URL = "{0:s}/anime/season/{1:d}/{2:s}"
    __SEAONS_NAME_TO_START_MONTH = {"Winter": 1, "Spring": 4, "Summer": 7, "Fall": 10}

    def __init__(self, season_name: str, year: int | str):
        """
        :param season_name: the name of the season. see __SEAONS_NAME_TO_START_MONTH keys.
        :type season_name: str
        :param year: the year of the season
        :type year: int or str
        """
        import time

        from pymal import exceptions

        self.year = int(year)
        self.season_name = season_name.title()
        if self.season_name not in self.__SEAONS_NAME_TO_START_MONTH:
            raise exceptions.NotASeasonError(season_name)
        self.url = self.__SEASON_URL.format(
            consts.HOST_NAME, self.year, self.season_name.lower()
        )

        self._is_loaded = False
        self.__animes = frozenset()

        month = str(self.__SEAONS_NAME_TO_START_MONTH[self.season_name])
        start_time_string = str(year) + " " + month
        self.start_time = time.strptime(start_time_string, "%Y %m")

    @property
    @decorators.load
    def animes(self) -> frozenset:
        """
        :return: all the animes in this season
        :rtype: frozenset
        """
        return self.__animes

    def reload(self):
        """
        fetching data.
        """
        import re

        import bs4

        from pymal import anime, global_functions

        data = global_functions.connect(self.url)
        html = bs4.BeautifulSoup(data, "lxml")
        anime_ids = set()

        for a in html.find_all("a", class_="link-title"):
            href = a.get("href", "")
            match = re.search(r"/anime/(\d+)", href)
            if match:
                anime_ids.add(int(match.group(1)))

        self.__animes = frozenset(anime.Anime(x) for x in anime_ids)
        self._is_loaded = True

    def __iter__(self):
        return iter(self.animes)

    def __len__(self):
        return len(self.animes)

    def __hash__(self):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(str(self.year).encode())
        hash_md5.update(self.season_name.encode())
        return int(hash_md5.hexdigest(), 16)

    def __repr__(self):
        return f"<{self.__class__.__name__:s} {self.season_name:s} {self.year:d}>"
