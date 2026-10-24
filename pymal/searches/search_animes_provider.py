__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from pymal.searches import search_provider


__all__ = ["SearchAnimesProvider"]


class SearchAnimesProvider(search_provider.SearchProvider):
    """
    Searching for animes.
    """

    _SEARCH_NAME = "anime"
    _SEARCHED_URL_SUFFIX = "/anime/"

    def _SEARCHED_OBJECT(self, mal_url: str):
        from pymal import anime

        mal_id = int(mal_url.split("/")[0])
        return anime.Anime(int(mal_id))
