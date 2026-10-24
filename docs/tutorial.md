# Tutorial

## Installation

Install from PyPI (the package is `pymal-ng`, you still `import pymal`):

```bash
pip install pymal-ng      # or: uv add pymal-ng
```

Or clone the repo and sync dependencies with `uv`:

```bash
git clone https://github.com/varyg1001/pymal
cd pymal
uv sync
```

Or add it to an existing project:

```bash
uv add git+https://github.com/varyg1001/pymal
```

---

## Browsing anime and manga

You don't need an account to read public MAL data.

```python
from pymal.anime import Anime
from pymal.manga import Manga

# Create by MAL ID — no network request yet
anime = Anime(1)       # Cowboy Bebop
manga = Manga(2)       # Berserk

# Data is fetched on first attribute access
print(anime.title)
print(anime.score)
print(anime.episodes)
print(anime.genres)

print(manga.title)
print(manga.chapters)
```

### Singleton behaviour

Constructing the same ID twice returns the same object — no duplicate requests:

```python
a = Anime(1)
b = Anime(1)
assert a is b   # True
```

---

## Working with an account

Changing your list, or reading a private one, needs a logged in account.
MyAnimeList's website login has a captcha, so pymal can't log in with a password.
There are two ways, and you only need one:

| | Official API (OAuth) | Browser cookies (experimental) |
|---|---|---|
| Setup | Create an API app once (about 5 minutes) | Export your browser's cookies (about 1 minute) |
| Keeps working | Tokens refresh themselves | Re-export when the session expires |
| What works | Everything, including tags, comments, dates, priority | Status, score and progress only |
| Stability | Documented and versioned | Undocumented website endpoints, can break |

**The official API.** Create an app at <https://myanimelist.net/apiconfig> (type *other*,
redirect URL such as `http://localhost/callback`) and use its **client ID**:

```python
from pymal.account import Account

account = Account("your-username")
account.authorize("your-client-id")   # shows a link; log in, allow, paste the address you land on
```

You only do this once: the tokens are saved to `~/.config/pymal/` and refreshed
automatically. The next time just `Account("your-username")` is enough.

**Browser cookies.** Log in to MyAnimeList in your browser, export its cookies with
an extension that writes a `cookies.txt` file, and give pymal the file (only the login
cookies are read from it):

```python
account = Account("your-username")
account.login_with_cookie("/path/to/cookies.txt", save=True)
```

Keep that file private: anyone who has it can act as you on MAL.
See the [account docs](api/account.md#logging-in) for the details and limits.

The public list of any account can be read without logging in.

### Reading your lists

```python
# These are lazy-loaded sets — fetched on first access
for entry in account.animes:
    print(entry.title, entry.my_status, entry.my_score)

for entry in account.animes.watching:     # also completed, on_hold, dropped, plan_to_watch
    print(entry.title, entry.my_completed_episodes)

for entry in account.mangas:
    print(entry.title, entry.my_completed_chapters)
```

### Adding an entry

```python
from pymal.anime import Anime

anime = Anime(1)
my_anime = anime.add(account)   # returns MyAnime (Plan to Watch)

account.animes.reload()
assert my_anime in account.animes
```

### Updating an entry

```python
my_anime.my_score = 9
my_anime.my_completed_episodes = 26
my_anime.update()
```

### Deleting an entry

```python
my_anime.delete()
```

---

## Set operations on lists

Account lists support standard set operations:

```python
my_list     = account.animes
friend_list = friend.animes

both        = my_list | friend_list          # union
shared      = my_list & friend_list          # intersection
only_mine   = my_list - friend_list          # difference
exclusive   = my_list ^ friend_list          # symmetric difference
```

---

## Seasons

```python
from pymal.seasons import Seasons

seasons = Seasons()
for season in seasons.seasons:
    print(season)
    for anime in season.animes:
        print(" ", anime.title)
```
