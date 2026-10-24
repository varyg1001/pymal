__authors__ = "tomer gelber, Aur Saraf, varyg"
__copyright__ = "(c) 2014, tomergelber; (c) 2026, varyg"
__license__ = "BSD License"
__contact__ = "https://github.com/varyg1001/pymal"

from urllib import request

import singleton_factory

from pymal import consts, decorators, global_functions


__all__ = ["Anime"]


class Anime(metaclass=singleton_factory.SingletonFactory):
    """
    Object that keeps all the anime data in MAL.

    :ivar image_url: :class:`str`
    :ivar title: :class:`str`
    :ivar english: :class:`str`
    :ivar synonyms: :class:`list` of :class:`str`
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
        self.__synonyms = []
        self.__japanese = ""
        self.__type = ""
        self.__status = ""
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

        self.__reviews = None
        self.__recommendations = None

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

        sock = global_functions._connect(self.image_url)
        data = io.BytesIO(sock.content)
        return Image.open(data)

    @property
    @decorators.load
    def english(self) -> str:
        return self.__english

    @property
    @decorators.load
    def synonyms(self) -> list:
        return list(self.__synonyms)

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
    def status(self) -> str:
        return self.__status

    @property
    @decorators.load
    def start_time(self) -> float | int:
        return self.__start_time

    @property
    @decorators.load
    def end_time(self) -> float | int:
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
    def rating(self) -> str:
        return self.__rating

    @property
    @decorators.load
    def episodes(self) -> int:
        return self.__episodes

    @staticmethod
    def __clean_title(title_span, h1) -> str:
        """The title without the English title that MAL puts inside the same tag."""
        if title_span is None:
            return h1.contents[0].strip()
        name = title_span.find(attrs={"itemprop": "name"}) or title_span
        first = name.find(string=True, recursive=False)
        return (first or name.get_text()).strip()

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
        self.__title = self.__clean_title(title_span, h1)

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
        self.__synonyms = []
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
                self.__synonyms = [x.strip() for x in value.split(",") if x.strip()]
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

        self.__score, self.__rank, self.__popularity = (
            global_functions.parse_header_stats(content_wrapper_div)
        )

        related = global_functions.parse_related_entries(content_wrapper_div)
        for label, target in self.related_str_to_set_dict.items():
            target.clear()
            target.update(related.get(label.rstrip(":").lower(), ()))

        # Data from main content
        main_content = contents[1]
        rightside = main_content.find("div", class_="rightside") or main_content

        # Getting synopsis (a <p> or <span> with itemprop="description")
        synopsis_tag = rightside.find(attrs={"itemprop": "description"})
        self.__synopsis = synopsis_tag.get_text().strip() if synopsis_tag else ""

        # Reviews and recommendations are separate pages: only fetched when asked for.
        self.__reviews = None
        self.__recommendations = None

        self._is_loaded = True

    @property
    @decorators.load
    def reviews(self) -> frozenset:
        """
        :return: the reviews of the first page of reviews; fetched on first use.
        :rtype: frozenset of :class:`inner_objects.review.Review`
        """
        if self.__reviews is None:
            # MAL needs a slug segment in the address; any text works
            from pymal.inner_objects import review

            div = global_functions.get_content_wrapper_div(
                f"{self.__mal_url}/_/reviews", global_functions.connect
            )
            self.__reviews = frozenset(
                map(review.Review, div.select("div.review-element"))
            )
        return self.__reviews

    @property
    @decorators.load
    def recommendations(self) -> frozenset:
        """
        :return: the recommendations of the first page; fetched on first use.
        :rtype: frozenset of :class:`inner_objects.recommendation.Recommendation`
        """
        if self.__recommendations is None:
            from pymal.inner_objects import recommendation

            div = global_functions.get_content_wrapper_div(
                f"{self.__mal_url}/_/userrecs", global_functions.connect
            )
            blocks = [
                t.parent
                for t in div.select("div.borderClass > table")
                if t.select_one(".picSurround")
            ]
            self.__recommendations = frozenset(map(recommendation.Recommendation, blocks))
        return self.__recommendations

    def add(self, account):
        """
        Adding this anime to the list of an account (as "plan to"), unless it is there.

        :param account: the account to add him self anime.
        :type account: :class:`account.Account`
        :rtype: :class:`account_objects.my_anime.MyAnime`
        :exception exceptions.MyAnimeListApiAddError: when failed.
        """
        from pymal.account_objects import my_anime

        return my_anime.MyAnime(self, account).add(account)

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
