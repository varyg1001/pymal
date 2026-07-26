# Tutorial

## Installation

Clone the repo and sync dependencies with `uv`:

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

Account-level operations (reading your list, adding/updating/deleting entries)
require authentication.

```python
from pymal.account import Account

account = Account("your-username", "your-password")
```

### Reading your lists

```python
# These are lazy-loaded sets — fetched on first access
for entry in account.animes:
    print(entry.title, entry.my_status, entry.my_score)

for entry in account.mangas:
    print(entry.title, entry.my_read_chapters)
```

### Adding an entry

```python
from pymal.anime import Anime

anime = Anime(1)
my_anime = anime.add(account)   # returns MyAnime

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
