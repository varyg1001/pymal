__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

from urllib import request

import niquests
import singleton_factory

from pymal import consts, decorators, global_functions


__all__ = ["Manga"]


class Manga(metaclass=singleton_factory.SingletonFactory):
    """
    Object that keeps all the anime data in MAL.

    :ivar title: :class:`str`
    :ivar image_url: :class:`str`
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
    :ivar chapters: :class:`int`
    :ivar volumes: :class:`int`
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
    """

    __GLOBAL_MAL_URL = request.urljoin(consts.HOST_NAME, "manga/{0:d}")
    __MY_MAL_ADD_URL = request.urljoin(consts.HOST_NAME, "api/mangalist/add/{0:d}.xml")

    def __init__(self, mal_id: int):
        """ """
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
        self.__score = 0.0
        self.__rank = 0
        self.__popularity = 0

        self._chapters = 0
        self._volumes = 0

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
        }

    @property
    def id(self) -> int:
        """
        :return: the mangas id.
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
        :return: The manga's image.
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
    def volumes(self) -> int:
        return self.__volumes

    @property
    @decorators.load
    def chapters(self) -> int:
        return self.__chapters

    def reload(self):
        """
        :exception exceptions.FailedToReloadError: when failed.
        """

        from pymal import exceptions

        # Getting content wrapper <div>
        content_wrapper_div = global_functions.get_content_wrapper_div(
            self.__mal_url, global_functions.connect
        )

        # Getting title <div>
        h1 = content_wrapper_div.h1
        self.__title = (h1.find("strong") or h1).get_text(strip=True)

        # Getting content <div>
        content_div = content_wrapper_div.find(name="div", attrs={"id": "content"})

        if content_div is None:
            raise exceptions.FailedToReloadError(content_wrapper_div)

        content_table = content_div.table
        tr = content_table.find(name="tr")
        contents = tr.find_all(name="td", recursive=False)

        # Data from side content
        side_content = contents[0]
        leftside = side_content.find("div", class_="leftside") or side_content

        # Getting manga image url <img>
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
        self.__volumes = 0
        self.__chapters = 0
        self.__status = ""
        self.__start_time = 0
        self.__end_time = 0
        self.__creators = {}
        self.__genres = {}
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
            elif label == "Volumes":
                self.__volumes = global_functions.make_counter(value)
            elif label == "Chapters":
                self.__chapters = global_functions.make_counter(value)
            elif label == "Status":
                self.__status = value
            elif label == "Published":
                self.__start_time, self.__end_time = (
                    global_functions.make_start_and_end_time(value)
                )
            elif label in ("Authors", "Serialization"):
                for a in div.find_all("a"):
                    self.__creators[a.get_text(strip=True)] = a["href"]
            elif label in ("Genres", "Genre", "Themes", "Theme", "Demographic"):
                for a in div.find_all("a"):
                    self.__genres[a.get_text(strip=True)] = a["href"]
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

        # Getting synopsis
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
    def MY_MAL_XML_TEMPLATE(self):
        return """<?xml version="1.0" encoding="UTF-8"?>
<entry>
	<chapter>{0:d}</chapter>
	<volume>{1:d}</volume>
	<status>{2:d}</status>
	<score>{3:d}</score>
	<downloaded_chapters>{4:d}</downloaded_chapters>
	<times_reread>{5:d}</times_reread>
	<reread_value>{6:d}</reread_value>
	<date_start>{7:s}</date_start>
	<date_finish>{8:s}</date_finish>
	<priority>{9:d}</priority>
	<enable_discussion>{10:d}</enable_discussion>
	<enable_rereading>{11:d}</enable_rereading>
	<comments>{12:s}</comments>
	<scan_group>{13:s}</scan_group>
	<tags>{14:s}</tags>
	<retail_volumes>{15:d}</retail_volumes>
</entry>"""

    def add(self, account):
        """
        :param account: the account to add him self manga.
        :type account: :class:`account.Account`

        :exception exceptions.MyAnimeListApiAddError: when failed.

        :rtype: :class:`account_objects.my_manga.MyManga`
        """
        from pymal import exceptions

        data = self.MY_MAL_XML_TEMPLATE.format(
            0,
            0,
            6,
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
            0,
        )
        xml = "".join(x.strip() for x in data.splitlines())
        delete_url = self.__MY_MAL_ADD_URL.format(self.id)
        ret = account.auth_connect(
            delete_url,
            data="data=" + xml,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if not ret.isdigit():
            raise exceptions.MyAnimeListApiAddError(ret)
        my_id = int(ret)

        from pymal.account_objects import my_manga

        return my_manga.MyManga(self, my_id, account)

    def __eq__(self, other):
        if isinstance(other, Manga):
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
        hash_md5.update(b"Manga")
        return int(hash_md5.hexdigest(), 16)

    def __repr__(self):
        title = "" if self.__title is None else " " + self.__title
        return f"<{self.__class__.__name__:s}{title:s} id={self.__id:d}>"

    def __format__(self, format_spec):
        return str(self).__format__(format_spec)
