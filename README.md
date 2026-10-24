# pymal

Python access to [MyAnimeList](https://myanimelist.net) data. Objects are
**lazy-loading**: MAL is only contacted when you first access a property.

Docs: <https://varyg1001.github.io/pymal/>

## Install

The package is published as `pymal-ng`; the import name is `pymal`.

```bash
pip install pymal-ng      # or: uv add pymal-ng
```

Requires Python 3.11–3.14.

## Quick start

```python
from pymal.anime import Anime

a = Anime(52991)          # no network call yet
print(a.title)            # first access fetches from MAL
print(a.score, a.episodes)
print(a.genres)
```

With an account (private lists, add/update/delete entries). MAL's website login has a
captcha, so pymal can't log in with a password; there are two ways:

```python
from pymal.account import Account

account = Account("your-username")

# 1. The official API (stable; everything works). Create an app once at
#    https://myanimelist.net/apiconfig and log in once; tokens are saved and refreshed.
account.authorize("your-client-id")

# 2. Experimental: the cookies of your browser (status, score and progress only).
account.login_with_cookie("cookies.txt")     # an export of your browser's cookies

for entry in account.animes:
    print(entry.title, entry.my_score)
entry = Anime(1887).add(account)             # add to the list (Plan to Watch)
entry.my_score = 9
entry.update()
```

Anime, manga, search, seasons and anyone's public list need no login. See the
[account docs](https://varyg1001.github.io/pymal/api/account/) for the details and limits.

Also available: `Manga`, `Seasons`/`Season`, and search via
`SearchAnimesProvider` / `SearchMangasProvider`. See the
[tutorial](https://varyg1001.github.io/pymal/tutorial/) and API reference.

## Development

```bash
git clone https://github.com/varyg1001/pymal
cd pymal
uv sync

uv run pytest                                     # offline tests; live account tests skip
MAL_USERNAME=you MAL_SESSIONID=cookies.txt uv run pytest      # include live account tests
# or MAL_CLIENT_ID=… MAL_ACCESS_TOKEN=…  (see docs/testing.md)
```

See [docs/changelog.md](docs/changelog.md) for release history.

## Credits

Originally created by **tomer gelber** and **Aur Saraf**
([pymal-developers/pymal](https://github.com/pymal-developers/pymal)).

The 1.0 revival was done mostly with AI, to fix breakage from outdated
dependencies and MAL's HTML changes.

## License

BSD 3-Clause — see [LICENSE](LICENSE).
