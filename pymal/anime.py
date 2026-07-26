__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

from urllib import request

import bs4
import niquests
import singleton_factory

from pymal import consts, decorators, global_functions


__all__ = ["Anime"]


class Anime(metaclass=singleton_factory.SingletonFactory):
    """
    Object that keeps all the anime data in MAL.

    :ivar image_url: :class:`str`
    :ivar title: :class:`str`
    :ivar english: :class:`str`
    :ivar synonyms: :class:`str`
    :ivar japanese: :class:`str`
    :ivar type: :class:`str`
    :ivar status: :class:`int`
    :ivar start_time: :class:`int`
    :ivar end_time: :class:`int`
    :ivar creators: :class:`dict`
    :ivar genres: :class:`dict`
    :ivar duration: :class:`int`
    :ivar score: :class:`float`
    :ivar rank: :class:`int`
    :ivar popularity: :class:`int`
    :ivar rating: :class:`str`
    :ivar episodes: :class:`int`
    :ivar synopsis: :class:`str`

    :ivar adaptations: :class:`frozenset`
    :ivar characters: :class:`frozenset`
    :ivar sequels: :class:`frozenset`
    :ivar prequels: :class:`frozenset`
    :ivar spin_offs: :class:`frozenset`
    :ivar alternative_versions: :class:`frozenset`
    :ivar side_stories: :class:`frozenset`
    :ivar summaries: :class:`frozenset`
    :ivar others: :class:`frozenset`
    :ivar parent_stories: :class:`frozenset`
    :ivar alternative_settings: :class:`frozenset`
    :ivar full_stories: :class:`frozenset`
    """

    __GLOBAL_MAL_URL = request.urljoin(consts.HOST_NAME, "anime/{0:d}")
    __MY_MAL_ADD_URL = request.urljoin(consts.HOST_NAME, "api/animelist/add/{0:d}.xml")

    def __init__(self, mal_id: int):
        """
        :param mal_id: the anime id in mal.
        :type mal_id: int
        """
        self.__id = mal_id
        self._is_loaded = False

        self.__mal_url = self.__GLOBAL_MAL_URL.format(self.__id)

        # Getting staff from html
        # staff from side content
        self.__title = ""
        self.__image_url = ""
        self.__english = ""
        self.__synonyms = ""
        self.__japanese = ""
        self.__type = ""
        self.__status = 0
        self.__start_time = 0
        self.__end_time = 0
        self.__creators = {}
        self.__genres = {}
        self.__duration = 0
        self.__score = 0.0
        self.__rank = 0
        self.__popularity = 0

        self.__rating = ""
        self.__episodes = 0

        # staff from main content
        # staff from row 1
        self.__synopsis = ""

        # staff from row 2
        self.__adaptations = set()
        self.__characters = set()
        self.__sequels = set()
        self.__prequels = set()
        self.__spin_offs = set()
        self.__alternative_versions = set()
        self.__side_stories = set()
        self.__summaries = set()
        self.__others = set()
        self.__parent_stories = set()
        self.__alternative_settings = set()
        self.__full_stories = set()

        self.related_str_to_set_dict = {
            "Adaptation:": self.__adaptations,
            "Character:": self.__characters,
            "Sequel:": self.__sequels,
            "Prequel:": self.__prequels,
            "Spin-off:": self.__spin_offs,
            "Alternative version:": self.__alternative_versions,
            "Side story:": self.__side_stories,
            "Summary:": self.__summaries,
            "Other:": self.__others,
            "Parent story:": self.__parent_stories,
            "Alternative setting:": self.__alternative_settings,
            "Full story:": self.__full_stories,
        }

    @property
    def id(self) -> int:
        """
        :return: The id of the anime.
        :rtype: :class:`int`
        """
        return self.__id

    @property
    @decorators.load
    def title(self) -> str:
        return self.__title

    @property
    @decorators.load
    def image_url(self) -> str:
        return self.__image_url

    def get_image(self):
        """
        :return: The image of the anime
        :rtype: :class:`PIL.Image.Image`
        """
        import io

        from PIL import Image

        sock = niquests.get(self.image_url)
        data = io.BytesIO(sock.content)
        return Image.open(data)

    @property
    @decorators.load
    def english(self) -> str:
        return self.__english

    @property
    @decorators.load
    def synonyms(self) -> str:
        return self.__synonyms

    @property
    @decorators.load
    def japanese(self) -> str:
        return self.__japanese

    @property
    @decorators.load
    def type(self) -> str:
        return self.__type

    @property
    @decorators.load
    def status(self) -> int:
        return self.__status

    @property
    @decorators.load
    def start_time(self) -> int:
        return self.__start_time

    @property
    @decorators.load
    def end_time(self) -> int:
        return self.__end_time

    @property
    @decorators.load
    def creators(self) -> dict:
        return self.__creators

    @property
    @decorators.load
    def genres(self) -> dict:
        return self.__genres

    @property
    @decorators.load
    def duration(self) -> int:
        return self.__duration

    @property
    @decorators.load
    def score(self) -> float:
        return self.__score

    @property
    @decorators.load
    def rank(self) -> int:
        return self.__rank

    @property
    @decorators.load
    def popularity(self) -> int:
        return self.__popularity

    @property
    @decorators.load
    def synopsis(self) -> str:
        return self.__synopsis

    # staff from main content
    @property
    @decorators.load
    def adaptations(self) -> frozenset:
        return frozenset(self.__adaptations)

    @property
    @decorators.load
    def characters(self) -> frozenset:
        return frozenset(self.__characters)

    @property
    @decorators.load
    def sequels(self) -> frozenset:
        return frozenset(self.__sequels)

    @property
    @decorators.load
    def prequels(self) -> frozenset:
        return frozenset(self.__prequels)

    @property
    @decorators.load
    def spin_offs(self) -> frozenset:
        return frozenset(self.__spin_offs)

    @property
    @decorators.load
    def alternative_versions(self) -> frozenset:
        return frozenset(self.__alternative_versions)

    @property
    @decorators.load
    def side_stories(self) -> frozenset:
        return frozenset(self.__side_stories)

    @property
    @decorators.load
    def summaries(self) -> frozenset:
        return frozenset(self.__summaries)

    @property
    @decorators.load
    def others(self) -> frozenset:
        return frozenset(self.__others)

    @property
    @decorators.load
    def parent_stories(self) -> frozenset:
        return frozenset(self.__parent_stories)

    @property
    @decorators.load
    def alternative_settings(self) -> frozenset:
        return frozenset(self.__alternative_settings)

    @property
    @decorators.load
    def full_stories(self) -> frozenset:
        return frozenset(self.__full_stories)

    @property
    @decorators.load
    def rating(self) -> int:
        return self.__rating

    @property
    @decorators.load
    def episodes(self) -> int:
        return self.__episodes

    def reload(self):
        """
        :exception exceptions.FailedToReloadError: when failed.
        """

        from pymal import exceptions

        # Getting content wrapper <div>
        content_wrapper_div = global_functions.get_content_wrapper_div(
            self.__mal_url, global_functions.connect
        )

        # Getting title
        h1 = content_wrapper_div.h1
        title_span = (
            h1.find("span", class_="h1-title")
            or h1.find("span", attrs={"itemprop": "name"})
            or h1.find("strong")
        )
        self.__title = (
            title_span.get_text(strip=True) if title_span else h1.contents[0].strip()
        )

        # Getting content <div>
        content_div = content_wrapper_div.find(name="div", attrs={"id": "content"})

        if content_div is None:
            raise exceptions.FailedToReloadError(content_wrapper_div)

        content_table = content_div.table

        tr = content_table.find(name="tr")
        contents = tr.find_all(name="td", recursive=False)

        # Data from side content
        side_content = contents[0]

        # Step into .leftside wrapper (new MAL layout)
        leftside = side_content.find("div", class_="leftside") or side_content

        # Getting anime image url <img>
        img = leftside.find(name="img")
        if img is None:
            self.__image_url = ""
        else:
            self.__image_url = img.get("data-src") or img.get("src") or ""

        # Reset all sidebar fields before label-based lookup
        self.__english = ""
        self.__synonyms = ""
        self.__japanese = ""
        self.__type = ""
        self.__episodes = 0
        self.__status = ""
        self.__start_time = 0
        self.__end_time = 0
        self.__creators = {}
        self.__genres = {}
        self.__duration = 0
        self.__rating = ""
        self.__score = 0.0
        self.__rank = 0
        self.__popularity = 0

        # Parse all metadata fields by label text (span.dark_text)
        for div in leftside.find_all("div"):
            span = div.find("span", class_="dark_text")
            if not span:
                continue
            label = span.get_text(strip=True).rstrip(":")
            value = div.get_text(strip=True)
            # Strip the label prefix from value
            label_with_colon = span.get_text(strip=True)
            if value.startswith(label_with_colon):
                value = value[len(label_with_colon) :].strip()

            if label == "English":
                self.__english = value
            elif label == "Synonyms":
                self.__synonyms = value
            elif label == "Japanese":
                self.__japanese = value
            elif label == "Type":
                self.__type = value
            elif label == "Episodes":
                self.__episodes = global_functions.make_counter(value)
            elif label == "Status":
                self.__status = value
            elif label == "Aired":
                self.__start_time, self.__end_time = (
                    global_functions.make_start_and_end_time(value)
                )
            elif label in ("Producers", "Studios", "Licensors"):
                for a in div.find_all("a"):
                    self.__creators[a.get_text(strip=True)] = a["href"]
            elif label in ("Genres", "Genre", "Themes", "Theme", "Demographic"):
                for a in div.find_all("a"):
                    self.__genres[a.get_text(strip=True)] = a["href"]
            elif label == "Duration":
                self.__duration = 0
                duration_parts = value.split(".")
                duration_parts = [p.strip() for p in duration_parts if p.strip()]
                for part in duration_parts:
                    tokens = part.split()
                    if len(tokens) >= 2 and tokens[1] in ("min", "hr"):
                        number = int(tokens[0])
                        if tokens[1] == "min":
                            self.__duration += number
                        elif tokens[1] == "hr":
                            self.__duration += number * 60
            elif label == "Rating":
                self.__rating = value
            elif label == "Score":
                try:
                    self.__score = float(value.split()[0])
                except (ValueError, IndexError):
                    self.__score = 0.0
            elif label == "Ranked":
                rank_str = value.lstrip("#").split()[0]
                try:
                    self.__rank = int(rank_str)
                except ValueError:
                    self.__rank = 0
            elif label == "Popularity":
                pop_str = value.lstrip("#").split()[0]
                try:
                    self.__popularity = int(pop_str)
                except ValueError:
                    self.__popularity = 0

        # Data from main content
        main_content = contents[1]
        rightside = main_content.find("div", class_="rightside") or main_content

        # Getting synopsis from modern layout <p itemprop="description"> or fallback h2
        synopsis_p = rightside.find("p", itemprop="description")
        if synopsis_p:
            self.__synopsis = synopsis_p.get_text().strip()
        else:
            synopsis_h2 = rightside.find(
                lambda tag: tag.name == "h2" and "Synopsis" in tag.get_text()
            )
            if synopsis_h2 and synopsis_h2.parent:
                self.__synopsis = synopsis_h2.parent.get_text(strip=True)
            else:
                self.__synopsis = ""

        reviews_tag = rightside.find(string="More reviews")
        if (
            reviews_tag is not None
            and reviews_tag.parent
            and "href" in reviews_tag.parent.attrs
        ):
            link_for_reviews = request.urljoin(
                consts.HOST_NAME, reviews_tag.parent["href"]
            )
            self.__parse_reviews(link_for_reviews)

        recommendations_tag = rightside.find(string="More recommendations")
        if (
            recommendations_tag is not None
            and recommendations_tag.parent
            and "href" in recommendations_tag.parent.attrs
        ):
            link_for_recommendations = request.urljoin(
                consts.HOST_NAME, recommendations_tag.parent["href"]
            )
            self.__parse_recommendations(link_for_recommendations)

        self._is_loaded = True

    def __parse_reviews(self, link_for_reviews: str):
        from pymal.inner_objects import review

        try:
            content_wrapper_div = global_functions.get_content_wrapper_div(
                link_for_reviews, global_functions.connect
            )
            content_div = content_wrapper_div.find(name="div", attrs={"id": "content"})
            tr = (
                content_div.table.find("tr")
                if content_div and content_div.table
                else None
            )
            if not tr:
                self.reviews = frozenset()
                return
            tds = tr.find_all(name="td", recursive=False)
            if len(tds) < 2:
                self.reviews = frozenset()
                return
            main_cell = tds[1]
            divs = main_cell.find_all(name="div", recursive=False)
            if len(divs) < 2:
                self.reviews = frozenset()
                return
            reviews_data_div = divs[1]
            reviews_data = reviews_data_div.find_all(name="div", recursive=False)[2:-2]
            self.reviews = frozenset(map(review.Review, reviews_data))
        except Exception:
            self.reviews = frozenset()

    def __parse_recommendations(self, link_for_recommendations: str):
        from pymal.inner_objects import recommendation

        try:
            content_wrapper_div = global_functions.get_content_wrapper_div(
                link_for_recommendations, global_functions.connect
            )
            content_div = content_wrapper_div.find(name="div", attrs={"id": "content"})
            tr = (
                content_div.table.find("tr")
                if content_div and content_div.table
                else None
            )
            if not tr:
                self.recommendations = frozenset()
                return
            tds = tr.find_all(name="td", recursive=False)
            if len(tds) < 2:
                self.recommendations = frozenset()
                return
            main_cell = tds[1]
            divs = main_cell.find_all(name="div", recursive=False)
            if len(divs) < 2:
                self.recommendations = frozenset()
                return
            recommendations_data_div = divs[1]
            recommendations_data = recommendations_data_div.find_all(
                name="div", recursive=False
            )[2:-1]
            self.recommendations = frozenset(
                map(recommendation.Recommendation, recommendations_data)
            )
        except Exception:
            self.recommendations = frozenset()

    @property
    def MY_MAL_XML_TEMPLATE(self) -> str:
        return """<?xml version="1.0" encoding="UTF-8"?>
<entry>
    <episode>{0:d}</episode>
    <status>{1:d}</status>
    <score>{2:d}</score>
    <downloaded_episodes>{3:d}</downloaded_episodes>
    <storage_type>{4:d}</storage_type>
    <storage_value>{5:f}</storage_value>
    <times_rewatched>{6:d}</times_rewatched>
    <rewatch_value>{7:d}</rewatch_value>
    <date_start>{8:s}</date_start>
    <date_finish>{9:s}</date_finish>
    <priority>{10:d}</priority>
    <enable_discussion>{11:d}</enable_discussion>
    <enable_rewatching>{12:d}</enable_rewatching>
    <comments>{13:s}</comments>
    <fansub_group>{14:s}</fansub_group>
    <tags>{15:s}</tags>
</entry>"""

    def add(self, account):
        """
        :param account: the account to add him self anime.
        :type account: :class:`account.Account`
        :rtype: :class:`account_objects.my_anime.MyAnime`
        :exception exceptions.MyAnimeListApiAddError: when failed.
        """
        from pymal import exceptions

        data = self.MY_MAL_XML_TEMPLATE.format(
            0,
            6,
            0,
            0,
            0,
            0,
            0,
            0,
            consts.MALAPI_NONE_TIME,
            consts.MALAPI_NONE_TIME,
            0,
            False,
            False,
            "",
            "",
            "",
        )
        xml = "".join(x.strip() for x in data.splitlines())
        delete_url = self.__MY_MAL_ADD_URL.format(self.id)
        ret = account.auth_connect(
            delete_url,
            data="data=" + xml,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        try:
            html_obj = bs4.BeautifulSoup(ret)
            if html_obj is None:
                raise exceptions.FailedToAddError(html_obj)

            head_obj = html_obj.head
            if head_obj is None:
                raise exceptions.FailedToAddError(head_obj)

            title_obj = head_obj.title
            if title_obj is None:
                raise exceptions.FailedToAddError(title_obj)

            data = title_obj.text
            if data is None:
                raise exceptions.FailedToAddError(data)

            my_id, string = data.split()
            if not my_id.isdigit():
                raise exceptions.FailedToAddError(my_id)
            if string != "Created":
                raise exceptions.FailedToAddError(string)
        except exceptions.FailedToAddError as err:
            raise exceptions.MyAnimeListApiAddError(ret) from err

        from pymal.account_objects import my_anime

        return my_anime.MyAnime(self, my_id, account)

    def __eq__(self, other):
        if isinstance(other, Anime):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        elif isinstance(other, str) and other.isdigit():
            return self.id == int(other)
        elif hasattr(other, "id"):
            return self.id == other.id
        return False

    def __hash__(self):
        import hashlib

        hash_md5 = hashlib.md5()
        hash_md5.update(str(self.id).encode())
        hash_md5.update(b"Anime")
        return int(hash_md5.hexdigest(), 16)

    def __repr__(self):
        title = "" if self.__title is None else " " + self.__title
        return f"<{self.__class__.__name__:s}{title:s} id={self.__id:d}>"

    def __format__(self, format_spec):
        return str(self).__format__(format_spec)
