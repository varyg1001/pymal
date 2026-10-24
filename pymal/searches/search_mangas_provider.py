__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from pymal.searches import search_provider


__all__ = ["SearchMangasProvider"]


class SearchMangasProvider(search_provider.SearchProvider):
    """
    Searching for mangas.
    """

    _SEARCH_NAME = "manga"
    _SEARCHED_URL_SUFFIX = "/manga/"

    def _SEARCHED_OBJECT(self, mal_url: str):
        from pymal import manga

        mal_id = int(mal_url.split("/")[0])
        return manga.Manga(int(mal_id))
