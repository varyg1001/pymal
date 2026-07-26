"""
Tests for the fixes applied in the fork:
  - lxml parser (html5lib removed)
  - New MAL sidebar layout (.leftside wrapper, label-based parsing)
  - h1 title now wrapped in <strong>
  - table has no <tbody>
  - niquests replaces requests
  - search_provider None guard on div_content

All tests use minimal inline HTML fixtures (no network calls) so they run
offline and never rely on a real MAL session.
"""

import unittest
from unittest.mock import Mock, patch

import bs4

from pymal import anime, global_functions


# ---------------------------------------------------------------------------
# Minimal HTML helpers
# ---------------------------------------------------------------------------


def _make_content_wrapper(
    title="Sousou no Frieren",
    english="Frieren: Beyond Journey's End",
    synonyms="",
    japanese="葬送のフリーレン",
    anime_type="TV",
    episodes="28",
    status="Finished Airing",
    aired="Oct 6, 2023 to Mar 22, 2024",
    producers="Madhouse",
    genres="Adventure, Drama, Fantasy",
    duration="24 min per ep.",
    rating="PG-13 - Teens 13 or older",
    score="9.07",
    ranked="#1",
    popularity="#24",
    image_src="https://cdn.myanimelist.net/images/anime/1015/138006.jpg",
    synopsis="After the party of heroes defeated the Demon King...",
):
    """
    Build a minimal contentWrapper div that mirrors the current MAL layout:
      - h1 > strong  (title)
      - table > tr > td (no tbody)
      - td > div.leftside > metadata divs
    Main content cell has exactly 2 top-level divs to satisfy the reload check.
    """

    def _meta(label, value_html):
        return (
            f'<div class="spaceit_pad">'
            f'<span class="dark_text">{label}:</span> {value_html}'
            f"</div>"
        )

    producer_links = "".join(
        f'<a href="/producer/11">{p.strip()}</a>' for p in producers.split(",")
    )
    genre_links = "".join(
        f'<a href="/genre/1/{g.strip().lower()}">{g.strip()}</a>'
        for g in genres.split(",")
    )

    optional_english = _meta("English", english) if english else ""
    optional_synonyms = _meta("Synonyms", synonyms) if synonyms else ""

    sidebar_html = f"""
    <div class="leftside">
        <div><a href="/anime/52991"><img src="{image_src}" /></a></div>
        {optional_english}
        {optional_synonyms}
        {_meta("Japanese", japanese)}
        {_meta("Type", anime_type)}
        {_meta("Episodes", episodes)}
        {_meta("Status", status)}
        {_meta("Aired", aired)}
        {_meta("Producers", producer_links)}
        {_meta("Genres", genre_links)}
        {_meta("Duration", duration)}
        {_meta("Rating", rating)}
        {_meta("Score", score)}
        {_meta("Ranked", ranked)}
        {_meta("Popularity", popularity)}
    </div>
    """

    # Main content: must have exactly 2 top-level divs in the main cell.
    # div[0] = placeholder, div[1] = the table with synopsis + related anime.
    main_html = f"""
    <div>placeholder</div>
    <div>
        <table>
            <tbody>
                <tr>
                    <td>
                        <h2>Synopsis</h2>
                        {synopsis}
                        <br/>
                    </td>
                </tr>
                <tr>
                    <td>
                        <br/>
                        <h2>Related Anime</h2>
                        <br/>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    """

    html = f"""
    <div id="contentWrapper">
        <h1 class="title-name h1_bold_none"><strong>{title}</strong></h1>
        <div id="content">
            <table>
                <tr>
                    <td>{sidebar_html}</td>
                    <td>{main_html}</td>
                </tr>
            </table>
        </div>
    </div>
    """
    return bs4.BeautifulSoup(html, "lxml").find(id="contentWrapper")


def _make_anime_instance(mal_id=52991):
    """Create a bare Anime instance bypassing SingletonFactory.__call__."""
    anm = object.__new__(anime.Anime)
    anm._Anime__id = mal_id
    anm._is_loaded = False
    anm._Anime__mal_url = f"https://myanimelist.net/anime/{mal_id}"
    for attr in [
        "__title",
        "__image_url",
        "__english",
        "__synonyms",
        "__japanese",
        "__type",
        "__status",
        "__rating",
        "__synopsis",
    ]:
        setattr(anm, f"_Anime{attr}", "")
    for attr in [
        "__start_time",
        "__end_time",
        "__duration",
        "__rank",
        "__popularity",
        "__episodes",
    ]:
        setattr(anm, f"_Anime{attr}", 0)
    anm._Anime__score = 0.0
    anm._Anime__creators = {}
    anm._Anime__genres = {}
    anm.related_str_to_set_dict = {
        "Adaptation:": set(),
        "Character:": set(),
        "Sequel:": set(),
        "Prequel:": set(),
        "Spin-off:": set(),
        "Alternative version:": set(),
        "Side story:": set(),
        "Summary:": set(),
        "Other:": set(),
        "Parent story:": set(),
        "Alternative setting:": set(),
        "Full story:": set(),
    }
    return anm


def _reload(anm, cwd):
    """Run reload() with get_content_wrapper_div mocked and review/rec skipped."""
    with (
        patch.object(global_functions, "get_content_wrapper_div", return_value=cwd),
        patch.object(anm, "_Anime__parse_reviews", return_value=None),
        patch.object(anm, "_Anime__parse_recommendations", return_value=None),
    ):
        anm.reload()


# ---------------------------------------------------------------------------
# Issue 1: lxml parser in global_functions
# ---------------------------------------------------------------------------


class TestLxmlParser(unittest.TestCase):
    """global_functions must use lxml, not html5lib."""

    def test_beautifulsoup_lxml_works(self):
        minimal = "<html><body><div id='myanimelist'></div></body></html>"
        soup = bs4.BeautifulSoup(minimal, "lxml")
        self.assertIsNotNone(soup.find(id="myanimelist"))

    def test_no_html5lib_in_global_functions(self):
        import inspect

        import pymal.global_functions as gf

        src = inspect.getsource(gf)
        self.assertNotIn("html5lib", src)
        self.assertIn("lxml", src)


# ---------------------------------------------------------------------------
# Issue 2: search_provider None guard
# ---------------------------------------------------------------------------


class TestSearchProviderNoneGuard(unittest.TestCase):
    """__get_list must return frozenset() when #content is absent."""

    def test_returns_empty_when_no_content_div(self):
        from pymal.searches import search_provider

        fake_resp = Mock()
        # url matches search_url so redirect branch is skipped
        fake_resp.url = "https://myanimelist.net/anime.php?q=test&show=0"
        fake_resp.text = "<html><body><p>No content div here</p></body></html>"

        with patch.object(global_functions, "_connect", return_value=fake_resp):
            # Access the mangled private method directly
            provider = search_provider.SearchProvider.__new__(
                search_provider.SearchProvider
            )
            provider._SEARCH_NAME = "anime"
            provider._SEARCHED_URL_SUFFIX = "/anime/"
            # Patch __SEARCH_URL property
            with patch.object(
                search_provider.SearchProvider,
                "_SearchProvider__SEARCH_URL",
                new_callable=lambda: property(
                    lambda _self: "https://myanimelist.net/anime.php"
                ),
            ):
                result = provider._SearchProvider__get_list("test", 0)

        self.assertIsInstance(result, frozenset)
        self.assertEqual(len(result), 0)


# ---------------------------------------------------------------------------
# Issue 3: h1 <strong> title fix
# ---------------------------------------------------------------------------


class TestAnimeTitleStrong(unittest.TestCase):
    def _extract_title(self, h1_html):
        soup = bs4.BeautifulSoup(h1_html, "lxml")
        h1 = soup.find("h1")
        return (h1.find("strong") or h1).get_text(strip=True)

    def test_title_from_strong_tag(self):
        html = (
            '<h1 class="title-name h1_bold_none"><strong>Sousou no Frieren</strong></h1>'
        )
        self.assertEqual(self._extract_title(html), "Sousou no Frieren")

    def test_title_fallback_no_strong(self):
        html = '<h1 class="title-name">Plain Title</h1>'
        self.assertEqual(self._extract_title(html), "Plain Title")

    def test_reload_sets_title_from_strong(self):
        anm = _make_anime_instance()
        cwd = _make_content_wrapper(title="Sousou no Frieren")
        _reload(anm, cwd)
        self.assertEqual(anm._Anime__title, "Sousou no Frieren")


# ---------------------------------------------------------------------------
# Issue 4: no <tbody> in table
# ---------------------------------------------------------------------------


class TestNoTbody(unittest.TestCase):
    def test_find_tr_without_tbody(self):
        html = "<table><tr><td>A</td><td>B</td></tr></table>"
        table = bs4.BeautifulSoup(html, "lxml").find("table")
        tr = table.find(name="tr")
        self.assertIsNotNone(tr)
        tds = tr.find_all(name="td", recursive=False)
        self.assertEqual(len(tds), 2)

    def test_find_tr_with_tbody(self):
        html = "<table><tbody><tr><td>X</td><td>Y</td></tr></tbody></table>"
        table = bs4.BeautifulSoup(html, "lxml").find("table")
        tr = table.find(name="tr")
        self.assertIsNotNone(tr)
        tds = tr.find_all(name="td", recursive=False)
        self.assertEqual(len(tds), 2)


# ---------------------------------------------------------------------------
# Issue 5: sidebar label-based parsing — full reload integration
# ---------------------------------------------------------------------------


class TestAnimeReloadSidebar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.anm = _make_anime_instance(52991)
        cwd = _make_content_wrapper(
            title="Sousou no Frieren",
            english="Frieren: Beyond Journey's End",
            synonyms="Frieren",
            japanese="葬送のフリーレン",
            anime_type="TV",
            episodes="28",
            status="Finished Airing",
            aired="Oct 6, 2023 to Mar 22, 2024",
            producers="Madhouse",
            genres="Adventure, Drama, Fantasy",
            duration="24 min per ep.",
            rating="PG-13 - Teens 13 or older",
            score="9.07",
            ranked="#1",
            popularity="#24",
            image_src="https://cdn.myanimelist.net/images/anime/1015/138006.jpg",
            synopsis="After the party of heroes defeated the Demon King...",
        )
        _reload(cls.anm, cwd)

    def test_title(self):
        self.assertEqual(self.anm._Anime__title, "Sousou no Frieren")

    def test_image_url(self):
        self.assertIn("cdn.myanimelist.net", self.anm._Anime__image_url)

    def test_english(self):
        self.assertEqual(self.anm._Anime__english, "Frieren: Beyond Journey's End")

    def test_synonyms(self):
        self.assertEqual(self.anm._Anime__synonyms, "Frieren")

    def test_japanese(self):
        self.assertEqual(self.anm._Anime__japanese, "葬送のフリーレン")

    def test_type(self):
        self.assertEqual(self.anm._Anime__type, "TV")

    def test_episodes(self):
        self.assertEqual(self.anm._Anime__episodes, 28)

    def test_status(self):
        self.assertEqual(self.anm._Anime__status, "Finished Airing")

    def test_rating(self):
        self.assertIn("PG-13", self.anm._Anime__rating)

    def test_duration(self):
        self.assertEqual(self.anm._Anime__duration, 24)

    def test_score(self):
        self.assertAlmostEqual(self.anm._Anime__score, 9.07, places=1)

    def test_rank(self):
        self.assertEqual(self.anm._Anime__rank, 1)

    def test_popularity(self):
        self.assertEqual(self.anm._Anime__popularity, 24)

    def test_genres_populated(self):
        self.assertGreater(len(self.anm._Anime__genres), 0)
        self.assertIn("Adventure", self.anm._Anime__genres)

    def test_creators_populated(self):
        self.assertGreater(len(self.anm._Anime__creators), 0)
        self.assertIn("Madhouse", self.anm._Anime__creators)

    def test_is_loaded(self):
        self.assertTrue(self.anm._is_loaded)


class TestAnimeReloadMissingOptionalFields(unittest.TestCase):
    """Reload must not crash when English/Synonyms are absent."""

    def test_missing_english_and_synonyms(self):
        anm = _make_anime_instance(99999)
        cwd = _make_content_wrapper(english="", synonyms="")
        _reload(anm, cwd)
        self.assertEqual(anm._Anime__english, "")
        self.assertEqual(anm._Anime__synonyms, "")


# ---------------------------------------------------------------------------
# Issue 7: niquests import — no stray `import requests`
# ---------------------------------------------------------------------------


class TestNiquestsImport(unittest.TestCase):
    def _check(self, module_path):
        import importlib
        import inspect

        mod = importlib.import_module(module_path)
        src = inspect.getsource(mod)
        self.assertIn("niquests", src, f"{module_path} should use niquests")
        self.assertNotIn(
            "import requests", src, f"{module_path} must not use `import requests`"
        )

    def test_global_functions(self):
        self._check("pymal.global_functions")

    def test_anime(self):
        self._check("pymal.anime")

    def test_manga(self):
        self._check("pymal.manga")

    def test_account(self):
        self._check("pymal.account")


# ---------------------------------------------------------------------------
# global_functions helpers
# ---------------------------------------------------------------------------


class TestGlobalFunctionsHelpers(unittest.TestCase):
    def test_make_counter_unknown(self):
        self.assertEqual(global_functions.make_counter("Unknown"), float("inf"))

    def test_make_counter_int(self):
        self.assertEqual(global_functions.make_counter("24"), 24)

    def test_make_start_and_end_time_single(self):
        start, end = global_functions.make_start_and_end_time("2023")
        self.assertEqual(start, end)

    def test_url_fixer_ascii(self):
        result = global_functions.url_fixer("https://myanimelist.net/anime/1")
        self.assertEqual(result, "https://myanimelist.net/anime/1")

    def test_check_side_content_div_match(self):
        html = '<div><span class="dark_text">English:</span> Lucky Star</div>'
        div = bs4.BeautifulSoup(html, "lxml").find("div")
        self.assertTrue(global_functions.check_side_content_div("English", div))

    def test_check_side_content_div_no_match(self):
        html = '<div><span class="dark_text">Japanese:</span> らき☆すた</div>'
        div = bs4.BeautifulSoup(html, "lxml").find("div")
        self.assertFalse(global_functions.check_side_content_div("English", div))


# ---------------------------------------------------------------------------
# Anime object behaviour (no network)
# ---------------------------------------------------------------------------


class TestAnimeObject(unittest.TestCase):
    def test_anime_id(self):
        a = anime.Anime(1887)
        self.assertEqual(a.id, 1887)

    def test_anime_repr_before_load(self):
        a = anime.Anime(8888)
        r = repr(a)
        self.assertIn("8888", r)
        self.assertIn("Anime", r)

    def test_anime_equality_int(self):
        a = anime.Anime(1887)
        self.assertEqual(a, 1887)

    def test_anime_equality_str(self):
        a = anime.Anime(1887)
        self.assertEqual(a, "1887")

    def test_anime_hash_stable(self):
        a = anime.Anime(1887)
        self.assertEqual(hash(a), hash(a))


if __name__ == "__main__":
    unittest.main()
