# Seasons

```python
from pymal.seasons import Seasons
from pymal.inner_objects.season import Season
```

## `Seasons()`

Singleton listing every season on MAL's archive page
(`/anime/season/archive`). Loaded lazily.

| Attribute | Type | Description |
|-----------|------|-------------|
| `seasons` | `frozenset[Season]` | All known seasons |

`reload()` re-fetches the archive.

## `Season(season_name, year)`

A single season, scraped from `/anime/season/<year>/<season>`.

| Attribute | Type | Description |
|-----------|------|-------------|
| `animes` | `frozenset[Anime]` | Anime airing that season |

`Season` is iterable and has `len()`; `reload()` re-fetches it.

## Example

```python
from pymal.inner_objects.season import Season

winter = Season("Winter", 2024)
for anime in winter:
    print(anime.title)
```
