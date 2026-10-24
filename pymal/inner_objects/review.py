__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import json
import re

from bs4 import NavigableString

from pymal import exceptions


class Review:
    """
    Review holds all the data from a review in MAL about an anime or manga.

    :ivar date: :class:`str`, when it was written, for example ``Jan 25, 2010``.
    :ivar account: :class:`account.Account` of the reviewer.
    :ivar helpful: :class:`int`, the number of reactions it got.
    :ivar rating: :class:`int`, the rating the reviewer gave, ``0`` if there isn't one.
    :ivar tags: :class:`tuple` of :class:`str`, like ``Recommended``.
    :ivar data: :class:`str`, the text of the review.
    """

    def __init__(self, div):
        """
        :param div: The ``div.review-element`` of the review to parse all the data from it.
        :type div: bs4.element.Tag
        """
        from pymal import account

        user_link = div.select_one("div.username a")
        date = div.select_one("div.update_at")
        text = div.select_one("div.text")
        if user_link is None or date is None or text is None:
            raise exceptions.FailedToParseError(div)

        self.date = date.get_text(strip=True)
        self.account = account.Account(user_link.get_text(strip=True))
        self.helpful = self.__reactions(div)

        rating = div.select_one("div.rating span.num")
        self.rating = int(rating.get_text(strip=True)) if rating else 0
        self.tags = tuple(
            tag.get_text(strip=True) for tag in div.select("div.tags div.tag")
        )

        # The page shows the start of the text and hides the rest: drop the "..." marker.
        for marker in text.select("span.js-visible"):
            marker.decompose()
        pieces = [
            "\n" if getattr(node, "name", None) == "br" else re.sub(r"\s+", " ", node)
            for node in text.descendants
            if getattr(node, "name", None) == "br" or isinstance(node, NavigableString)
        ]
        lines = [
            re.sub(r" {2,}", " ", line).strip() for line in "".join(pieces).split("\n")
        ]
        self.data = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()

    @staticmethod
    def __reactions(div) -> int:
        try:
            return int(json.loads(div.get("data-reactions", "{}")).get("num", 0))
        except (ValueError, TypeError):
            return 0

    def __repr__(self):
        return (
            f"<{self.__class__.__name__:s} written by {self.account.username:s} "
            f"on {self.date:s}, rated {self.rating:d} ({self.helpful:d} reactions)>"
        )
