__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import re

from pymal import exceptions


class Recommendation:
    """
    Recommendation holds all the data from a recommendation in MAL about an anime or manga.

    :ivar recommended: :class:`anime.Anime` or :class:`manga.Manga` that is recommended.
    :ivar recommends: :class:`dict` of :class:`account.Account` to the text they wrote.
        Only the users MAL shows on the page are in it ("and 78 more users" aren't).
    """

    def __init__(self, div):
        """
        :param div: The ``div.borderClass`` of one recommendation (it holds a table).
        :type div: bs4.element.Tag
        """
        from pymal import account, anime, manga

        link = div.select_one("div.picSurround a[href]")
        match = re.search(r"/(anime|manga)/(\d+)", link["href"]) if link else None
        if match is None:
            raise exceptions.FailedToParseError(div)
        kind = anime.Anime if match.group(1) == "anime" else manga.Manga
        self.recommended = kind(int(match.group(2)))

        self.recommends = {}
        for text in div.select("div.detail-user-recs-text"):
            user = text.parent.select_one("a[href*='/profile/']")
            if user is not None:
                self.recommends[account.Account(user.get_text(strip=True))] = (
                    text.get_text(" ", strip=True)
                )

    @property
    def recommended_anime(self):
        """The recommended title (kept for the old name)."""
        return self.recommended

    def __repr__(self):
        return (
            f"<{self.__class__.__name__:s} for {self.recommended!r} "
            f"by {len(self.recommends):d} users>"
        )
