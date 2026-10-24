__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

import re
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

# MAL advertises HTTP/3 (Alt-Svc) but doesn't serve it reliably: skip it instead of
# letting the first request fail and retry.
__SESSION = niquests.Session(disable_http3=True)


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
    method: str | None = None,
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
    :param method: the HTTP method; ``POST`` if there is data and ``GET`` otherwise.
    :type method: :class:`str` or :class:`None`

    :return: the respond of the connection
    :rtype: :class:`niquests.Response`
    :raises exceptions.SiteUnavailableError: when MAL can't be reached or keeps
        answering with 429/5xx after :data:`consts.RETRY_NUMBER` attempts.
    """
    if headers is None:
        headers = {}

    url = url_fixer(url)

    headers.setdefault("User-Agent", consts.USER_AGENT)
    method = (method or ("POST" if data is not None else "GET")).upper()
    # A POST may already have been applied by the server, so it is only retried
    # when the connection itself failed, never on a timeout or a server error.
    # GET, PUT and DELETE are idempotent and always safe to retry.
    is_post = method == "POST"
    reason = ""
    for attempt in range(consts.RETRY_NUMBER):
        if attempt:
            time.sleep(consts.RETRY_SLEEP * attempt)
        try:
            sock = session.request(
                method,
                url,
                data=data,
                headers=headers,
                auth=auth,
                timeout=consts.REQUEST_TIMEOUT,
            )
        except niquests.exceptions.ConnectionError as e:
            reason = f"connection failed: {e}"
            continue
        except niquests.exceptions.Timeout as e:
            reason = f"timed out: {e}"
            if is_post:
                break
            continue
        if sock.status_code in consts.UNAVAILABLE_STATUS_CODES:
            reason = f"HTTP {sock.status_code}"
            if is_post:
                break
            continue
        return sock
    raise exceptions.SiteUnavailableError(url, reason)


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


def fetch_public_list_json(url: str) -> list:
    """
    Fetch every entry of a public MAL ``load.json`` list; MAL returns it in pages.

    :param url: the list url with a ``status`` query and no ``offset``.
    :raises exceptions.SiteUnavailableError: when MAL can't be reached.
    :return: all the entries (dicts); empty if the list isn't readable.
    """
    items = []
    while True:
        sock = _connect(f"{url}&offset={len(items)}")
        if sock.status_code != 200:
            break
        try:
            page = sock.json()
        except ValueError:
            break
        if not isinstance(page, list) or not page:
            break
        items.extend(page)
    return items


def parse_header_stats(root: bs4.element.Tag) -> tuple[float, int, int]:
    """
    Read the score, rank and popularity from the stats header of an anime/manga page.

    :return: ``(score, rank, popularity)``; ``0`` for every value MAL doesn't show.
    """

    def number(tag) -> int:
        match = re.search(r"\d[\d,]*", tag.get_text()) if tag else None
        return int(match.group().replace(",", "")) if match else 0

    score_tag = root.find(class_="score-label")
    try:
        score = float(score_tag.get_text(strip=True)) if score_tag else 0.0
    except ValueError:
        score = 0.0  # "N/A"
    rank = number(root.select_one("span.numbers.ranked strong"))
    popularity = number(root.select_one("span.numbers.popularity strong"))
    return score, rank, popularity


def parse_related_entries(root: bs4.element.Tag) -> dict:
    """
    Read the "Related Entries" section of an anime/manga page: the first relations are
    tiles, the rest are rows of a table.

    :return: ``{relation: set of Anime/Manga}`` with the relation in lower case,
        for example ``{"sequel": {...}, "side story": {...}}``.
    """
    from pymal import anime, manga

    related = {}

    def add(relation: str, href: str):
        match = re.search(r"/(anime|manga)/(\d+)", href or "")
        if match:
            obj = anime.Anime if match.group(1) == "anime" else manga.Manga
            related.setdefault(relation.strip().rstrip(":").lower(), set()).add(
                obj(int(match.group(2)))
            )

    container = root.find(class_="related-entries")
    if container is None:
        return related
    for entry in container.select("div.entry"):
        relation_tag = entry.find(class_="relation")
        link = entry.select_one("div.title a") or entry.find("a", href=True)
        if relation_tag is not None and link is not None:
            add(relation_tag.get_text(" ", strip=True).split("(")[0], link.get("href"))
    for row in container.select("table.entries-table tr"):
        label = row.find("td")
        if label is not None:
            for link in row.select("ul.entries a[href]"):
                add(label.get_text(" ", strip=True), link.get("href"))
    return related


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
    for attempt in range(consts.RETRY_NUMBER):
        if attempt:  # wait only before trying again
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
    counter_string = counter_string.strip().replace(",", "")
    if not counter_string.isdigit():
        return float("inf")
    return int(counter_string)
