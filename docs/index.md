# pymal

A Python library for interacting with [MyAnimeList](https://myanimelist.net).

## Features

- **Lazy loading** — data is fetched from MAL only when first accessed, then cached
- **Singleton objects** — `Anime(1)` always returns the same object; no duplicate requests
- **Anime & Manga** — read metadata (title, score, episodes, genres, etc.)
- **Account integration** — manage your anime/manga list (add, update, delete entries)
- **Set operations** — intersect, union, diff your anime/manga lists

## Quick start

```python
from pymal.anime import Anime

anime = Anime(1)          # Cowboy Bebop
print(anime.title)        # fetches data on first access
print(anime.score)
print(anime.episodes)
```

With an account:

```python
from pymal.account import Account

account = Account("your-username", "your-password")

for entry in account.animes:
    print(entry.title, entry.my_status)
```

## Installation

```bash
git clone https://github.com/varyg1001/pymal
cd pymal
uv sync
```

## Requirements

- Python 3.10–3.14
- [`niquests`](https://pypi.org/project/niquests/) — HTTP client
- [`lxml`](https://pypi.org/project/lxml/) — HTML parser
- [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/)
