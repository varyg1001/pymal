# Manga

```python
from pymal.manga import Manga
```

## Constructor

```python
Manga(mal_id: int)
```

Returns a singleton. Data is fetched lazily on first attribute access.

## Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `int` | MAL manga ID |
| `title` | `str` | Main title |
| `english` | `str` | English title (if available) |
| `japanese` | `str` | Japanese title |
| `synonyms` | `str` | Alternative titles |
| `image_url` | `str` | URL of the cover image |
| `type` | `str` | e.g. `"Manga"`, `"Novel"`, `"One-shot"` |
| `volumes` | `int` | Volume count (`0` = unknown) |
| `chapters` | `int` | Chapter count (`0` = unknown) |
| `status` | `str` | e.g. `"Publishing"`, `"Finished"` |
| `score` | `float` | MAL community score |
| `rank` | `int` | MAL rank |
| `popularity` | `int` | MAL popularity rank |
| `genres` | `dict` | `{name: url}` mapping |
| `authors` | `dict` | `{name: url}` mapping |
| `start_time` | `str` | Publish start date |
| `end_time` | `str` | Publish end date |

## Methods

### `reload()`
Force re-fetch all data from MAL.

### `add(account) -> MyManga`
Add this manga to the given account's list. Returns a
[`MyManga`](my_manga.md) object.

## Example

```python
from pymal.manga import Manga

manga = Manga(2)
print(manga.title)    # "Berserk"
print(manga.score)
print(manga.chapters)
```
