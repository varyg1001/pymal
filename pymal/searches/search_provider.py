__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from urllib import parse

import bs4
import singleton_factory

from pymal import consts, exceptions, global_functions


class RankedResults(frozenset):
    """
    The results of a search: a :class:`frozenset` that iterates in the order MAL ranked
    them (best match first), so ``list(results)[:10]`` are the ten best matches.
    """

    def __new__(cls, items=()):
        ranked = tuple(dict.fromkeys(items))
        obj = super().__new__(cls, ranked)
        obj._ranked = ranked
        return obj

    def __iter__(self):
        return iter(self._ranked)

    def __contains__(self, item):
        # by equality, so an id works too: ``5114 in results``
        return item in self._ranked

    def __reduce__(self):
        return (self.__class__, (self._ranked,))


class SearchProvider(metaclass=singleton_factory.SingletonFactory):
    """
    A search engine.
    Change the following properties and it will search for you:
     - _SEARCH_NAME
     - _SEARCHED_URL_SUFFIX
     - _SEARCHED_OBJECT
    """

    _SEARCH_NAME = ""
    _PREFIX_TYPE = None  # type name of the prefix.json API; defaults to _SEARCH_NAME
    _SEARCHED_URL_SUFFIX = ""
    _SEARCHED_OBJECT = object

    @staticmethod
    def _prefix_key(item: dict) -> str | None:
        """What _SEARCHED_OBJECT is built from, given one prefix.json item."""
        item_id = item.get("id")
        return str(item_id) if item_id else None

    @property
    def __SEARCH_URL(self):
        return parse.urljoin(consts.HOST_NAME, self._SEARCH_NAME + ".php")

    def __make_url(self, search_line: str, show_number: int) -> str:
        params = {"q": search_line, "show": show_number}
        url_parts = list(parse.urlparse(self.__SEARCH_URL))
        query = dict(parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = parse.urlencode(query)
        return parse.urlunparse(url_parts)

    def __get_list(self, search_line: str, show_number: int) -> frozenset:
        search_url = self.__make_url(search_line, show_number)

        sock = global_functions._connect(search_url)

        if sock.url != search_url:
            return frozenset([parse.urlsplit(sock.url).path])

        html = bs4.BeautifulSoup(sock.text, "lxml")
        div_content = html.find(name="div", attrs={"id": "content"})
        if div_content is None:
            return frozenset()
        divs_pic = div_content.findAll(name="div", attrs={"class": "picSurround"})
        return frozenset(x.a["href"] for x in divs_pic)

    def search(self, search_line: str) -> RankedResults:
        """
        :param search_line: the search line to find
        :type search_line: str
        :return: the found results, best match first when iterated
        :rtype: :class:`RankedResults` (a frozenset)
        :exception exceptions.SiteUnavailableError: when MAL can't be reached.
        """
        import contextlib

        # Try modern MAL prefix search JSON API endpoint
        prefix_type = self._PREFIX_TYPE or self._SEARCH_NAME
        prefix_url = f"{consts.HOST_NAME}/search/prefix.json?type={prefix_type}&keyword={parse.quote(search_line)}"
        # An outage is reported at once; any other trouble falls back to the old search.
        try:
            sock = global_functions._connect(prefix_url)
            data = sock.json() if sock.status_code == 200 else {}
        except exceptions.SiteUnavailableError:
            raise
        except Exception:
            data = {}
        results = []
        for category in data.get("categories", []):
            if category.get("type") == prefix_type or not prefix_type:
                for item in category.get("items", []):
                    key = self._prefix_key(item)
                    if key:
                        with contextlib.suppress(Exception):
                            results.append(self._SEARCHED_OBJECT(key))
        if results:
            return RankedResults(results)

        # Fallback to legacy scraping method
        ret = set()
        current_index = 0
        res = self.__get_list(search_line, current_index)
        while res - ret:
            ret.update(res)
            current_index += len(res)
            res = self.__get_list(search_line, current_index)

        results = set()
        for x in ret:
            parts = x.split(self._SEARCHED_URL_SUFFIX)
            if len(parts) > 1:
                with contextlib.suppress(Exception):
                    results.add(self._SEARCHED_OBJECT(parts[1]))
        return RankedResults(results)
