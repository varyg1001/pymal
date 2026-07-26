__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

from urllib import parse

import bs4
import singleton_factory

from pymal import consts, global_functions


class SearchProvider(metaclass=singleton_factory.SingletonFactory):
    """
    A search engine.
    Change the following properties and it will search for you:
     - _SEARCH_NAME
     - _SEARCHED_URL_SUFFIX
     - _SEARCHED_OBJECT
    """

    _SEARCH_NAME = ""
    _SEARCHED_URL_SUFFIX = ""
    _SEARCHED_OBJECT = object

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

    def search(self, search_line: str) -> frozenset:
        """
        :param search_line: the search line to find
        :type search_line: str
        :return: the found results
        :rtype: frozenset
        """
        import contextlib

        # Try modern MAL prefix search JSON API endpoint
        prefix_url = f"{consts.HOST_NAME}/search/prefix.json?type={self._SEARCH_NAME}&keyword={parse.quote(search_line)}"
        with contextlib.suppress(Exception):
            sock = global_functions._connect(prefix_url)
            if sock.status_code == 200:
                data = sock.json()
                results = set()
                for category in data.get("categories", []):
                    if category.get("type") == self._SEARCH_NAME or not self._SEARCH_NAME:
                        for item in category.get("items", []):
                            item_id = item.get("id")
                            if item_id:
                                with contextlib.suppress(Exception):
                                    results.add(self._SEARCHED_OBJECT(str(item_id)))
                if results:
                    return frozenset(results)

        # Fallback to legacy scraping method
        ret = set()
        current_index = 0
        res = self.__get_list(search_line, current_index)
        while len(res) > 0:
            ret.update(res)
            current_index += len(res)
            res = self.__get_list(search_line, current_index)
        ret.update(res)

        results = set()
        for x in ret:
            parts = x.split(self._SEARCHED_URL_SUFFIX)
            if len(parts) > 1:
                with contextlib.suppress(Exception):
                    results.add(self._SEARCHED_OBJECT(parts[1]))
        return frozenset(results)
