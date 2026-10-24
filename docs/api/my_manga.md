# MyManga

```python
from pymal.account_objects.my_manga import MyManga
```

Wraps a [`Manga`](manga.md) with the data of one account about it. Any attribute
not listed below is proxied to the wrapped `Manga`.
You get a `MyManga` back when you call `manga.add(account)` or when iterating
`account.mangas`. It needs a [logged in](account.md#logging-in) account.

Changing an attribute only changes it locally; call `update()` to send it to MAL.

## Additional attributes

Values are loaded from MAL on first use (already filled when obtained via `account.mangas`).

| Attribute | Type | Description |
|-----------|------|-------------|
| `in_list` | `bool` | Whether the account has this manga in its list |
| `my_status` | `int` | 1=Reading, 2=Completed, 3=On-Hold, 4=Dropped, 6=Plan to Read (`0` if not in the list) |
| `my_score` | `int` | Score, 0 (none) to 10 |
| `my_completed_chapters` | `int` | Chapters read |
| `my_completed_volumes` | `int` | Volumes read |
| `my_is_rereading` | `bool` | Whether you're rereading |
| `my_tags` | `frozenset` | Tags (you can assign any set) |
| `my_comments` | `str` | Comments |
| `my_priority` | `int` | 0 (low) to 2 (high) |
| `my_start_date` | `str` | Start date as `yyyymmdd`; `00000000` if unset |
| `my_end_date` | `str` | Finish date as `yyyymmdd`; `00000000` if unset |
| `my_times_reread` | `int` | Times reread |
| `my_reread_value` | `int` | Reread value, 0 to 5 |

Assigning an invalid value raises `ValueError`.

With the experimental [cookie login](account.md#experimental-without-the-api-with-a-browser-cookie) only `my_status`, `my_score`, `my_completed_chapters` and `my_completed_volumes` are read from MAL and sent back; the other attributes keep their defaults and `update()` leaves them as they are on MAL.

## Methods

### `my_reload()`
Re-fetch your data about this manga from MAL.

### `update()`
Send your changes to MAL. The manga is added to your list if it isn't there.

### `delete()`
Remove this entry from your list.

### `increase() -> bool` / `increase_volume() -> bool`
Add one read chapter / volume (Plan to Read becomes Reading). `False` if everything was read.

### `set_completed() -> bool`
Mark all chapters (and volumes) read and the status Completed. `False` if the chapter count is unknown.

### `is_completed`
`True` if all chapters were read.

## Example

```python
from pymal.account import Account

account = Account("your-username")
entry = next(iter(account.mangas))

print(entry.title)                  # proxied to the wrapped Manga
print(entry.my_completed_chapters)

entry.my_score = 9
entry.update()
```
