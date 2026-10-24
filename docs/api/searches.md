# Searches

```python
from pymal.searches.search_animes_provider import SearchAnimesProvider
from pymal.searches.search_mangas_provider import SearchMangasProvider
from pymal.searches.search_accounts_provider import SearchAccountsProvider
```

Each provider is a singleton that searches MAL for one kind of object.
They all subclass `SearchProvider`.

| Provider | Returns |
|----------|---------|
| `SearchAnimesProvider` | [`Anime`](anime.md) objects |
| `SearchMangasProvider` | [`Manga`](manga.md) objects |
| `SearchAccountsProvider` | accounts |

The results are a `frozenset` that iterates in the order MAL ranked them (best match first),
so `list(results)[:10]` are the ten best matches. `5114 in results` works with an ID too.

## Methods

### `search(search_line: str) -> frozenset`
Search MAL and return the matching objects. Uses MAL's `prefix.json` endpoint
and falls back to the legacy search page scraping if that fails.

The same searches are available as module functions: `pymal.searches.search_animes(text)`,
`search_mangas(text)` and `search_accounts(text)`.

## Example

```python
from pymal.searches.search_animes_provider import SearchAnimesProvider

for anime in SearchAnimesProvider().search("frieren"):
    print(anime.id, anime.title)
```
