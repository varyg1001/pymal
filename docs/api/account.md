# Account

```python
from pymal.account import Account
```

## Constructor

```python
Account(username: str, password: str)
```

Returns a singleton keyed by username. Authenticates lazily when
first needed.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `username` | `str` | MAL username |
| `animes` | `AccountAnimes` | Your anime list (lazy-loaded set) |
| `mangas` | `AccountMangas` | Your manga list (lazy-loaded set) |
| `friends` | `AccountFriends` | Your friends list (lazy-loaded set) |

## List objects

`account.animes` and `account.mangas` are set-like objects that support:

```python
len(account.animes)              # number of entries
anime in account.animes          # membership test (Anime, MyAnime, or int ID)
account.animes.reload()          # re-fetch from MAL

# Set operations
account.animes | friend.animes   # union
account.animes & friend.animes   # intersection
account.animes - friend.animes   # difference
account.animes ^ friend.animes   # symmetric difference
```

## Example

```python
from pymal.account import Account

account = Account("your-username", "your-password")

# Iterate your anime list
for entry in account.animes:
    print(entry.title, entry.my_score)

# Check membership
from pymal.anime import Anime
anime = Anime(1)
print(anime in account.animes)  # True / False
```
