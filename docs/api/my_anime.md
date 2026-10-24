# MyAnime

```python
from pymal.account_objects.my_anime import MyAnime
```

Wraps an [`Anime`](anime.md) with the data of one account about it. Any attribute
not listed below is proxied to the wrapped `Anime`.
You get a `MyAnime` back when you call `anime.add(account)` or when iterating
`account.animes`. It needs a [logged in](account.md#logging-in) account.

Changing an attribute only changes it locally; call `update()` to send it to MAL.

## Additional attributes

Values are loaded from MAL on first use (already filled when obtained via `account.animes`).

| Attribute | Type | Description |
|-----------|------|-------------|
| `in_list` | `bool` | Whether the account has this anime in its list |
| `my_status` | `int` | 1=Watching, 2=Completed, 3=On-Hold, 4=Dropped, 6=Plan to Watch (`0` if not in the list) |
| `my_score` | `int` | Score, 0 (none) to 10 |
| `my_completed_episodes` | `int` | Episodes watched |
| `my_is_rewatching` | `bool` | Whether you're rewatching |
| `my_tags` | `frozenset` | Tags (you can assign any set) |
| `my_comments` | `str` | Comments |
| `my_priority` | `int` | 0 (low) to 2 (high) |
| `my_start_date` | `str` | Start date as `yyyymmdd`; `00000000` if unset |
| `my_end_date` | `str` | Finish date as `yyyymmdd`; `00000000` if unset |
| `my_times_rewatched` | `int` | Times rewatched |
| `my_rewatch_value` | `int` | Rewatch value, 0 to 5 |

Assigning an invalid value raises `ValueError`.

With the experimental [cookie login](account.md#experimental-without-the-api-with-a-browser-cookie) only `my_status`, `my_score` and `my_completed_episodes` are read from MAL and sent back; the other attributes keep their defaults and `update()` leaves them as they are on MAL.

## Methods

### `my_reload()`
Re-fetch your data about this anime from MAL.

### `update()`
Send your changes to MAL. The anime is added to your list if it isn't there.

### `delete()`
Remove this entry from your list.

### `increase() -> bool`
Add one watched episode (Plan to Watch becomes Watching). `False` if everything was watched.

### `set_completed() -> bool`
Mark all episodes watched and the status Completed. `False` if the episode count is unknown.

### `is_completed`
`True` if all episodes were watched.

## Example

```python
from pymal.account import Account

account = Account("your-username")
entry = next(iter(account.animes))

print(entry.title)                  # proxied to the wrapped Anime
print(entry.my_score)
print(entry.my_completed_episodes)

entry.my_score = 10
entry.update()
```
