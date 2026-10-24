# Changelog

## 2.0.0 — 2026-10

### Breaking changes
- `Anime.synonyms` and `Manga.synonyms` are a `list` of strings (MAL's comma separated list, split) instead of one string. This is what [pptu](https://github.com/encoding-hun/pptu) already expects (`synonyms[0]`); with a string it got the first character.
- **Login moved to MAL's official API.** MyAnimeList's website login now has a captcha, so `Account(username, password)`, `change_password()` and `auth_connect()` are gone. Log in with `Account(username).authorize(client_id)` once (official API; tokens are saved and refreshed automatically), or with the experimental `Account.login_with_cookie(...)` (see the [account docs](api/account.md#logging-in) for both). `Account.login(client_id, access_token, ...)` takes tokens you already have, `Account.api(...)` calls any API v2 endpoint.
- `MyAnime` / `MyManga` are rewritten on the API (and about 1,400 lines smaller). The constructor is `MyAnime(mal_id, account)`. Removed, because the API doesn't have them: `my_id`, `my_storage_type`, `my_storage_value`, `my_download_episodes`, `my_fan_sub_groups`, `my_enable_discussion`, `my_downloaded_chapters`, `my_retail_volumes`, `to_xml()`, `increase_downloaded()` and `set_completed_download()`. New: `in_list`.
- Invalid values assigned to `my_*` attributes raise `ValueError` (was `RuntimeError`); `my_priority` is 0–2 and `my_status` only accepts 1, 2, 3, 4 and 6.
- `increase()` simply adds one episode/chapter (and turns Plan to Watch/Read into Watching/Reading).
- `Account.is_auth` means "has an access token".
- `anime.add(account)` / `manga.add(account)` no longer reset an entry that is already in the list.
- Dropped the undocumented `map_of_lists` of the list objects.

### New
- `Account.authorize` always shows MAL's login screen and refuses (saving nothing) if the browser was logged in as a different account than the one you named.
- **Experimental:** `Account.login_with_cookie()` uses the `MALSESSIONID` cookie of a browser where you are logged in, when you don't have an API app. It reads private lists and can add, change and delete entries, limited to status, score and progress, through MAL's undocumented website endpoints (see the account docs for the caveats). It takes the `MALSESSIONID` value, a dict, a whole `Cookie` header, or the path of a browser `cookies.txt` export, and adds the `is_logged_in=1` flag cookie MAL checks. Every write is read back from the list and fails loudly if it didn't happen.
- `Account.me()`, `Account.suggestions()` and `Account.anime_ranking()`.
- Public lists of any account still work without logging in (bare entries).
- Account lists are filled from the API in one request per 1,000 entries, including all the data of each entry.
- `exceptions.SiteUnavailableError` and automatic retries when MAL is down (see Fixes)
- Related entries (`sequels`, `prequels`, `adaptations`, `spin_offs`, ...) on `Anime` and `Manga` are now actually filled in; before, they were always empty
- `SearchAccountsProvider` / `Account.search` works again (MAL's type is `user`, results are keyed by username)

### Changes
- **Faster lookups:** a cold `Anime(...)`/`Manga(...)` load now takes about 1 s instead of 3.5 s. pymal no longer sleeps before the first request of a page (only before a retry), and `reviews` and `recommendations` are fetched when you ask for them, not on every load. They are now properties on `Anime` and `Manga` (before they were attributes that often didn't exist).
- Account lists load every page of the list (before: only the first 300 entries), and a MAL outage is no longer silently an empty list
- Minimum Python is now 3.11 (3.10 dropped)
- `pillow` requirement raised to `>=13.0.0`
- Replaced legacy `singleton3` with `singleton-factory`
- Published to PyPI as `pymal-ng`

### Fixes
- Reviews and recommendations work again: both parsers were written for pages MAL has since redesigned and silently returned nothing. `Anime.reviews`/`Manga.reviews` now hold the 20 reviews of the first reviews page, `recommendations` the recommendations of the first page. `Review` has `account`, `date`, `rating`, `helpful`, `tags` and `data` (`watched` and `when_written` no longer exist on MAL); `Recommendation.recommended` is the recommended title (`recommended_anime` still works), and recommendations of manga are `Manga` objects.
- Related entries (`sequels`, `side_stories`, `alternative_versions`, ...) were missing every relation that MAL puts in its table below the first tiles, and relation names are matched ignoring case (`Side Story` / `Side story`).
- A manga title could include its English title (`One Punch-ManOne-Punch Man`).
- Search results keep MAL's ranking (best match first) instead of an arbitrary set order, `id in results` works, and an outage during a search is reported at once instead of being retried through the old search.
- MAL being down is now handled: requests time out after 15 s, retry on connection errors, timeouts and HTTP 429/5xx, then raise the new `exceptions.SiteUnavailableError` (POSTs are never retried after the server may have received them)
- `score`, `rank` and `popularity` were parsed from the wrong place (often `0` or off by the footnote digit); they now come from the page header stats
- Manga `synopsis` returned the whole page text; it now returns only the synopsis
- Set operations on account lists were wrong: `list & x` always returned an empty set and `list - x` returned the whole list
- Account profile parsing matches MAL's current pages: `user_id`, the avatar (`image_url`/`get_image()`) and the friends list (`account.friends`) were all broken
- Legacy search fallback could loop forever if MAL ignored the paging parameter
- `make_counter` crashed on counts like `1,100` or `?`
- `get_image()` now uses the shared retrying/timeout HTTP layer
- Corrected return annotations: `status`/`rating` are `str`, `start_time`/`end_time` are timestamps
- `make_time` now handles `Not available` and other unparseable dates safely (returns `inf`)
- `tests/account_objects/test_account_mangas.py` filename typo fixed, so it is collected again

---

## 1.0.0 — 2026-07

### Breaking changes
- Dropped Python 2 support entirely (was already broken)
- Removed `six` dependency
- Removed `html5lib` dependency

### Fixes
- **HTML parser**: switched from `html5lib` to `lxml` — resolves dependency conflicts and speeds up parsing
- **HTTP client**: replaced `requests` with `niquests` (drop-in replacement with modern TLS/HTTP2 support)
- **Sidebar parsing** (`anime.py`): rewrote from brittle index-based access to label-based lookup via `span.dark_text` — fixes all fields broken by MAL's layout update
- **Title extraction** (`anime.py`): fixed `IndexError` caused by MAL wrapping the title in a `<strong>` tag inside `<h1>`
- **Table parsing** (`anime.py`): fixed `AttributeError` caused by MAL removing `<tbody>` from tables
- **Search API** (`searches/search_provider.py`): migrated from legacy `anime.php?q=...` endpoints to MAL's modern `prefix.json` API with fallback protection
- **Season Scraping** (`seasons.py`, `inner_objects/season.py`): migrated from dead `malupdater.com` third-party server to native MyAnimeList season (`/anime/season/<year>/<season>`) and archive listing pages
- **User Account Lists** (`account_animes.py`, `account_mangas.py`): updated to MAL's modern JSON list endpoints (`load.json`)
- **`ReloadedSet`**: fixed `collections.Set` → `collections.abc.Set` (removed in Python 3.10)
- **`HOST_NAME`**: updated `http://` → `https://` (MAL enforces HTTPS)

### Infrastructure
- Migrated build system from `setup.py` to `uv_build` (`pyproject.toml`)
- Replaced `nosetests` with `pytest`
- Added offline test suite (`tests/test_fixes.py`, 40 tests)
- Docs migrated from Sphinx/RST to MkDocs Material
- Deleted obsolete files: `upload_new_version.bat`, `.travis.yml`, `MANIFEST.in`, legacy HTML fixtures

---

## 0.5b4 — 2014

Initial public release.
