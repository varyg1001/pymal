# pymal

Programmatic access to [MyAnimeList](https://myanimelist.net) data in Python.
Objects are **lazy-loading** — MAL is only contacted when you first access a property.

---

## Quick start

```python
from pymal import anime

# Lazy — no network call yet
a = anime.Anime(52991)

# First property access triggers the MAL fetch
print(a.title)    # "Sousou no Frieren"
print(a.score)    # 9.07
print(a.episodes) # 28
print(a.genres)   # {'Adventure': '...', 'Drama': '...', 'Fantasy': '...'}
print(a.english)  # "Frieren: Beyond Journey's End"
print(a.japanese) # "葬送のフリーレン"
```

---

## Installation

### With uv (recommended)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # install uv once

git clone https://github.com/varyg1001/pymal
cd pymal
uv sync
```

### With pip

```bash
git clone https://github.com/varyg1001/pymal
cd pymal
pip install -e .
```

---

## Requirements

- Python `>=3.11, <3.15`
- [`uv`](https://github.com/astral-sh/uv) (recommended) or pip

Key runtime dependencies (full list in `pyproject.toml`):

| Package | Purpose |
|---------|---------|
| `niquests[socks,utls]` | HTTP client (modern drop-in for `requests`) |
| `beautifulsoup4` + `lxml` | HTML parsing |
| `singleton-factory` | Object singleton lifecycle |

---

## Search & Endpoint Features

- **Search API**: Search providers (`SearchAnimesProvider`, `SearchMangasProvider`) automatically query MyAnimeList's modern `prefix.json` API endpoint (`/search/prefix.json`), falling back gracefully if needed.
- **Seasons**: Seasonal anime lookups (`Season`, `Seasons`) scrape directly from native MyAnimeList season pages (`/anime/season/<year>/<season>`) and the archive listing (`/anime/season/archive`).
- **User Lists**: Account anime and manga lists (`AccountAnimes`, `AccountMangas`) utilize MAL's modern JSON list endpoints (`load.json`).

---

## Running tests

```bash
# Offline suite — no network or account needed (40 tests)
uv run pytest tests/test_fixes.py -v

# Full suite — account tests auto-skip unless credentials are set
MAL_USERNAME=you MAL_PASSWORD=secret uv run pytest -v
```

---

## Project structure

```
pymal/
├── pymal/
│   ├── anime.py                  # Anime object
│   ├── manga.py                  # Manga object
│   ├── account.py                # MAL account & auth
│   ├── global_functions.py       # HTTP + HTML parsing helpers
│   ├── account_objects/          # MyAnime, MyManga, lists, friends
│   ├── searches/                 # Search providers
│   └── inner_objects/            # Season, recommendation, etc.
├── tests/
│   ├── test_fixes.py             # Offline test suite (40 tests)
│   └── account_objects/          # Live account tests (skipped without creds)
├── docs/                         # MkDocs documentation source
├── mkdocs.yml                    # Docs config (GitHub Pages)
├── pyproject.toml                # Build config & pinned deps (uv_build)
└── uv.lock                       # Lockfile — commit this
```

---

## What changed in v1.0.0

The original project (v0.5b4–v0.6) had broken against MAL's HTML updates and
modern Python. v1.0.0 brings it back to life:

| # | Area | Fix |
|---|------|-----|
| 1 | Parser | `html5lib` → `lxml` (no more `six` conflict) |
| 2 | HTTP | `requests` → `niquests[socks,utls]` (HTTP/2, QUIC, modern TLS) |
| 3 | Sidebar | Full rewrite from brittle index-based to label-based lookup (`span.dark_text`) |
| 4 | Title | Fixed `IndexError` — MAL now wraps `<h1>` content in `<strong>` |
| 5 | Table | Fixed `AttributeError` — MAL removed `<tbody>` from tables |
| 6 | Search | Migrated from legacy `anime.php` to MAL's modern `prefix.json` API |
| 7 | Seasons | Migrated from dead `malupdater.com` to native MAL `/anime/season` pages |
| 8 | User Lists | Updated `AccountAnimes` & `AccountMangas` to MAL's `load.json` API |
| 9 | Build | `setup.py` → `uv_build` + `pyproject.toml` |
| 10 | Tests | New offline suite with 40 tests; account tests skip without credentials |
| 11 | Docs | Migrated from Sphinx/RST to MkDocs Material (GitHub Pages) |
| 12 | Cleanup | Removed `.travis.yml`, `MANIFEST.in`, `upload_new_version.bat`, dead HTML fixtures |

Also fixed latent bugs: `==` used instead of `=` in `my_anime.py` and
`my_manga.py` meant `download_episodes` and `times_rewatched` were never
actually stored.

---

## Credits

### Original authors

pymal was created and developed by:

- **tomer gelber** — [tomergelber@gmail.com](mailto:tomergelber@gmail.com)
- **Aur Saraf** — [sonoflilit@gmail.com](mailto:sonoflilit@gmail.com)

Original repository: [pymal-developers/pymal](https://github.com/pymal-developers/pymal)

### v1.0.0

The update was made with mostly AI. The main reason for the update is the errors cause by the old things used in the last released version. I still feel that this is the easiest way to get info from MAL, even with the original version, since MAL has not changed much.

---

## License

BSD License — see original repository for full text.
