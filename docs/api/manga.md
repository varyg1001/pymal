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
| `synonyms` | `list[str]` | Alternative titles (MAL's comma separated list, split) |
| `image_url` | `str` | URL of the cover image |
| `type` | `str` | e.g. `"Manga"`, `"Novel"`, `"One-shot"` |
| `volumes` | `int` | Volume count (`inf` = unknown) |
| `chapters` | `int` | Chapter count (`inf` = unknown) |
| `status` | `str` | e.g. `"Publishing"`, `"Finished"` |
| `score` | `float` | MAL community score |
| `rank` | `int` | MAL rank |
| `popularity` | `int` | MAL popularity rank |
| `genres` | `dict` | `{name: url}` mapping |
| `creators` | `dict` | `{name: url}` mapping (authors/artists) |
| `synopsis` | `str` | Synopsis text |
| `start_time` | `float` | Publish start as a Unix timestamp (`inf` if unknown) |
| `end_time` | `float` | Publish end as a Unix timestamp (`inf` if unknown) |

Related entries (`adaptations`, `characters`, `sequels`, `prequels`, `spin_offs`,
`alternative_versions`, `side_stories`, `summaries`, `others`, `parent_stories`,
`alternative_settings`) are `frozenset`s.

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
Download the cover and return a `PIL.Image.Image`.

### `reload()`
Force re-fetch all data from MAL.

### `add(account) -> MyManga`
Add this manga to the given account's list (as Plan to Read) unless it is already there. Returns a
[`MyManga`](my_manga.md) object.

## Example

```python
from pymal.manga import Manga

manga = Manga(2)
print(manga.title)    # "Berserk"
print(manga.score)
print(manga.chapters)
```
