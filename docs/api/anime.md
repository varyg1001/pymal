# Anime

```python
from pymal.anime import Anime
```

## Constructor

```python
Anime(mal_id: int)
```

Returns a singleton — calling `Anime(1)` twice returns the same object.
Data is not fetched until the first attribute access.

## Attributes

All attributes below trigger a network fetch on first access (lazy loading).

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | MAL anime ID |
| `title` | `str` | Main title |
| `english` | `str` | English title (if available) |
| `japanese` | `str` | Japanese title |
| `synonyms` | `str` | Alternative titles |
| `image_url` | `str` | URL of the poster image |
| `type` | `str` | e.g. `"TV"`, `"Movie"`, `"OVA"` |
| `episodes` | `int` | Episode count (`0` = unknown) |
| `status` | `str` | e.g. `"Finished Airing"` |
| `score` | `float` | MAL community score |
| `rank` | `int` | MAL rank |
| `popularity` | `int` | MAL popularity rank |
| `rating` | `str` | Age rating |
| `duration` | `int` | Duration in minutes per episode |
| `genres` | `dict` | `{name: url}` mapping |
| `creators` | `dict` | `{name: url}` mapping (studios/producers) |
| `start_time` | `str` | Air start date |
| `end_time` | `str` | Air end date |

## Methods

### `reload()`
Force re-fetch all data from MAL.

### `add(account) -> MyAnime`
Add this anime to the given account's list. Returns a
[`MyAnime`](my_anime.md) object.

## Example

```python
from pymal.anime import Anime

anime = Anime(1)
print(anime.title)    # "Cowboy Bebop"
print(anime.score)    # 8.75
print(anime.episodes) # 26
print(anime.genres)   # {"Action": "...", "Space": "..."}
```
