__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

import time
from urllib import request

import bs4
import niquests

from pymal import consts, exceptions


__all__ = [
    "connect",
    "get_next_index",
    "make_set",
    "check_side_content_div",
    "get_content_wrapper_div",
]

__SESSION = niquests.Session()


def url_fixer(url: str) -> str:
    url = url.encode("utf-8")
    for i in range(128, 256):
        url = url.replace(bytes([i]), f"%{i:X}".encode())
    return url.decode("utf-8")


def _connect(
    url: str,
    data: str | None = None,
    headers: dict | None = None,
    auth=None,
    session: niquests.Session = __SESSION,
) -> niquests.Response:
    """
    :param url: url
    :type url: :class:`str`
    :param data: data to post
    :type data: :class:`str`
    :param headers: headers to send
    :type headers: :class:`dict` or :class:`None`
    :param auth: the authenticate for the session.
    :type auth: :class:`niquests.auth.HTTPBasicAuth`
    :param session: the session to connect to, otherwise using the default ones.
    :type session: :class:`niquests.Session`

    :return: the respond of the connection
    :rtype: :class:`niquests.Response`
    """
    if headers is None:
        headers = {}

    url = url_fixer(url)

    headers["User-Agent"] = consts.USER_AGENT
    if data is not None:
        sock = session.post(url, data=data, headers=headers, auth=auth)
    else:
        sock = session.get(url, headers=headers, auth=auth)
    return sock


def connect(
    url: str, data: str | None = None, headers: dict | None = None, auth=None
) -> str:
    """
    :param url: url
    :param data: data to post
    :param headers: headers to send
    :rtype : responded data
    """
    return _connect(url, data, headers, auth).text.strip()


def get_next_index(i: int, list_of_tags: list) -> int:
    """
    return the i after the next <br/>

    :type i: int
    :param i: an index
    :type list_of_tags: list
    :param list_of_tags: list of tags to check the i on
    :rtype: int
    """
    while i < len(list_of_tags) and list_of_tags[i].name != "br":
        i += 1
    return i + 1


def make_set(self_set: set, i: int, list_of_tags: list) -> int:
    """
    return the index after the next <br/> and inserting all the link until it.

    :type self_set: set
    :param self_set: a list to append links to
    :type i: int
    :param i: an index
    :type list_of_tags: list
    :param list_of_tags: list of tags to check the index on
    :rtype: int
    """
    from pymal import anime, manga

    n_i = get_next_index(i, list_of_tags)
    for j in range(i + 1, n_i, 2):
        if list_of_tags[j].name != "a":
            exceptions.FailedToParseError(list_of_tags[j].name)
        tag_href = list_of_tags[j]["href"]
        if "/anime/" in tag_href:
            obj = anime.Anime
            splitter = "/anime/"
        elif "/manga/" in tag_href:
            obj = manga.Manga
            splitter = "/manga/"
        else:
            self_set.add(request.urljoin(consts.HOST_NAME, list_of_tags[j]["href"]))
            continue
        obj_id = tag_href.split(splitter)[1].split("/")[0]
        if not obj_id.isdigit():
            continue
        self_set.add(obj(int(obj_id)))
    return n_i


def check_side_content_div(expected_text: str, div_node: bs4.element.Tag):
    span_node = div_node.span
    if span_node is None:
        raise exceptions.FailedToParseError(div_node)
    expected_text += ":"
    if span_node["class"] != ["dark_text"]:
        return False
    return expected_text == span_node.text.strip()


def __get_myanimelist_div(url: str, connection_function) -> bs4.element.Tag:
    got_robot = False
    for _ in range(consts.RETRY_NUMBER):
        time.sleep(consts.RETRY_SLEEP)
        data = connection_function(url)
        html = bs4.BeautifulSoup(data, "lxml").html
        robots = (
            html.head.find(name="meta", attrs={"name": "robots"}) if html.head else None
        )
        if robots and "noindex" in robots.get("content", "").lower():
            got_robot = True
            continue
        div = html.body.find(name="div", attrs={"id": "myanimelist"})
        if div is not None:
            return div
    if got_robot:
        raise exceptions.GotRobotError()
    raise exceptions.FailedToParseError("my anime list div wasn't found")


def get_content_wrapper_div(url: str, connection_function) -> bs4.element.Tag:
    myanimelist_div = __get_myanimelist_div(url, connection_function)

    # Getting content wrapper <div>
    content_wrapper_div = myanimelist_div.find(name="div", attrs={"id": "contentWrapper"})
    if content_wrapper_div is None:
        raise exceptions.FailedToParseError(myanimelist_div)
    return content_wrapper_div


def make_start_and_end_time(start_and_end_string: str) -> tuple:
    """
    getting mal site airing / publishing format and return it as tuple(int, int)
    """
    split = start_and_end_string.split("to")
    if len(split) == 1:
        start_time = split[0].strip()
        end_time = start_time
    else:
        start_time, end_time = split
    start_time, end_time = start_time.strip(), end_time.strip()
    return make_time(start_time), make_time(end_time)


def make_time(time_string: str) -> float | int:
    """
    getting mal site time string format and return it as int/float
    """
    if (
        not time_string
        or time_string == "?"
        or time_string == consts.MALAPPINFO_NONE_TIME
        or time_string.lower() in ("not available", "n/a", "unknown", "none")
    ):
        return float("inf")
    if time_string.isdigit():
        return int(time_string)
    for fmt in (consts.SHORT_SITE_FORMAT_TIME, consts.LONG_SITE_FORMAT_TIME):
        try:
            return time.mktime(time.strptime(time_string, fmt))
        except ValueError:
            pass
    try:
        ts = time_string[:4] + time_string[4:].replace("00", "01")
        return time.mktime(time.strptime(ts, consts.MALAPPINFO_FORMAT_TIME))
    except ValueError:
        return float("inf")


def make_counter(counter_string: str) -> int | float:
    """
    getting mal site counter string format and return it as int
    """
    if counter_string == "Unknown":
        return float("inf")
    return int(counter_string)
