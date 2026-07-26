# MyAnime

```python
from pymal.account_objects.my_anime import MyAnime
```

Extends [`Anime`](anime.md) with per-account tracking data.
You get a `MyAnime` back when you call `anime.add(account)` or
when iterating `account.animes`.

## Additional attributes

All attributes below require `my_reload()` to be called first
(or are already populated when obtained via `account.animes`).

| Attribute | Type | Description |
|-----------|------|-------------|
| `my_id` | `int` | Entry ID in your list |
| `my_status` | `int` | Watch status (1=Watching, 2=Completed, 3=On-Hold, 4=Dropped, 6=Plan to Watch) |
| `my_score` | `int` | Your score (0–10) |
| `my_completed_episodes` | `int` | Episodes watched |
| `my_is_rewatching` | `bool` | Whether you're rewatching |
| `my_tags` | `frozenset` | Your tags |
| `my_comments` | `str` | Your comments |
| `my_priority` | `int` | Priority |
| `my_start_date` | `str` | Your watch start date |
| `my_end_date` | `str` | Your watch end date |
| `my_times_rewatched` | `int` | Times rewatched |
| `my_rewatch_value` | `int` | Rewatch value |
| `my_storage_type` | `int` | Storage type |
| `my_storage_value` | `float` | Storage value |
| `my_download_episodes` | `int` | Downloaded episodes |
| `my_fan_sub_groups` | `str` | Fansub groups |

## Methods

### `my_reload()`
Fetch personal tracking data from MAL.

### `update()`
Push local changes back to MAL.

### `delete()`
Remove this entry from your list.

### `to_xml() -> str`
Serialize entry to MAL API XML format.

## Example

```python
from pymal.account import Account

account = Account("your-username", "your-password")
entry = list(account.animes)[0]

entry.my_reload()
print(entry.title)                  # inherited from Anime
print(entry.my_score)
print(entry.my_completed_episodes)

entry.my_score = 10
entry.update()
```
