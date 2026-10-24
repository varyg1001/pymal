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
| `synonyms` | `list[str]` | Alternative titles (MAL's comma separated list, split) |
| `image_url` | `str` | URL of the poster image |
| `type` | `str` | e.g. `"TV"`, `"Movie"`, `"OVA"` |
| `episodes` | `int` | Episode count (`inf` = unknown) |
| `status` | `str` | e.g. `"Finished Airing"` |
| `score` | `float` | MAL community score |
| `rank` | `int` | MAL rank |
| `popularity` | `int` | MAL popularity rank |
| `rating` | `str` | Age rating |
| `synopsis` | `str` | Synopsis text |
| `duration` | `int` | Duration in minutes per episode |
| `genres` | `dict` | `{name: url}` mapping |
| `creators` | `dict` | `{name: url}` mapping (studios/producers) |
| `start_time` | `float` | Air start as a Unix timestamp (`inf` if unknown) |
| `end_time` | `float` | Air end as a Unix timestamp (`inf` if unknown) |

Related entries (`adaptations`, `characters`, `sequels`, `prequels`, `spin_offs`,
`alternative_versions`, `side_stories`, `summaries`, `others`, `parent_stories`,
`alternative_settings`, `full_stories`) are `frozenset`s.

### Reviews and recommendations

`reviews` and `recommendations` are `frozenset`s that are fetched from their own
pages the first time you use them (a title is not slower to load because of them),
then cached. They hold the first page of each: 20 reviews, and about 60–170 recommendations.

| Review | |
|---|---|
| `account` | the reviewer, an `Account` |
| `date` | when it was written, e.g. `"Jan 25, 2010"` |
| `rating` | the reviewer's rating, `0` if none |
| `helpful` | number of reactions it got |
| `tags` | tuple of tags such as `"Recommended"` |
| `data` | the text |

| Recommendation | |
|---|---|
| `recommended` | the recommended `Anime`/`Manga` |
| `recommends` | `{Account: text}` of the users MAL lists on the page |

## Methods

### `get_image()`
Download the poster and return a `PIL.Image.Image`.

### `reload()`
Force re-fetch all data from MAL.

### `add(account) -> MyAnime`
Add this anime to the given account's list (as Plan to Watch) unless it is already there. Returns a
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
